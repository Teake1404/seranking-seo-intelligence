#!/usr/bin/env python3
"""
Advanced SEO Insights MCP Server
Provides comprehensive SEO analysis including anomaly detection, 
competitive analysis, opportunity scoring, and trend analysis.
"""

import json
import re
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListResourcesRequest, 
    ListResourcesResult, ReadResourceRequest, ReadResourceResult
)

# Initialize the MCP server
server = Server("seo-insights-mcp")

@dataclass
class SEOData:
    """Container for SEO data"""
    rankings: List[Dict[str, Any]]
    competitors: List[Dict[str, Any]]
    backlinks: Dict[str, Any]
    domain: str
    market: str
    timestamp: datetime

@dataclass
class AnomalyResult:
    """Result of anomaly detection"""
    keyword: str
    current_position: int
    expected_position: float
    severity: str
    z_score: float
    change_type: str

@dataclass
class OpportunityResult:
    """SEO opportunity analysis result"""
    keyword: str
    current_position: int
    search_volume: int
    difficulty: int
    opportunity_score: float
    potential_traffic: int
    priority: str

class SEOInsightsAnalyzer:
    """Advanced SEO analysis engine"""
    
    def __init__(self):
        self.anomaly_threshold = 2.0  # Z-score threshold for anomalies
        self.opportunity_threshold = 0.7  # Opportunity score threshold
        
    def detect_anomalies(self, current_rankings: Dict[str, Any], 
                        historical_data: List[Dict[str, Any]]) -> List[AnomalyResult]:
        """Detect ranking anomalies using statistical analysis"""
        anomalies = []
        
        if not historical_data:
            return anomalies
            
        # Build keyword history
        keyword_history = {}
        for record in historical_data:
            keyword = record.get('keyword')
            position = record.get('position')
            if keyword and position and position > 0:
                if keyword not in keyword_history:
                    keyword_history[keyword] = []
                keyword_history[keyword].append(position)
        
        # Analyze current rankings for anomalies
        for keyword, info in current_rankings.get('keywords', {}).items():
            current_pos = info.get('position')
            if not current_pos or current_pos <= 0:
                continue
                
            history = keyword_history.get(keyword)
            if history and len(history) >= 3:  # Need at least 3 data points
                avg_pos = np.mean(history)
                std_dev = np.std(history)
                
                if std_dev > 0:
                    z_score = abs((current_pos - avg_pos) / std_dev)
                    
                    if z_score > self.anomaly_threshold:
                        severity = "high" if z_score > 3.0 else "medium"
                        change_type = "improvement" if current_pos < avg_pos else "decline"
                        
                        anomalies.append(AnomalyResult(
                            keyword=keyword,
                            current_position=current_pos,
                            expected_position=avg_pos,
                            severity=severity,
                            z_score=z_score,
                            change_type=change_type
                        ))
        
        return anomalies
    
    def analyze_opportunities(self, rankings_data: List[Dict[str, Any]], 
                           competitors_data: List[Dict[str, Any]]) -> List[OpportunityResult]:
        """Analyze SEO opportunities based on keyword data"""
        opportunities = []
        
        for keyword_data in rankings_data:
            keyword = keyword_data.get('keyword')
            position = keyword_data.get('position', 0)
            volume = keyword_data.get('volume', 0)
            difficulty = keyword_data.get('difficulty', 0)
            cpc = keyword_data.get('cpc', 0)
            
            if not keyword or position <= 0:
                continue
                
            # Calculate opportunity score
            opportunity_score = self._calculate_opportunity_score(
                position, volume, difficulty, cpc
            )
            
            if opportunity_score > self.opportunity_threshold:
                potential_traffic = self._estimate_traffic_potential(position, volume)
                priority = self._determine_priority(opportunity_score, volume)
                
                opportunities.append(OpportunityResult(
                    keyword=keyword,
                    current_position=position,
                    search_volume=volume,
                    difficulty=difficulty,
                    opportunity_score=opportunity_score,
                    potential_traffic=potential_traffic,
                    priority=priority
                ))
        
        # Sort by opportunity score
        opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)
        return opportunities[:20]  # Top 20 opportunities
    
    def _calculate_opportunity_score(self, position: int, volume: int, 
                                   difficulty: int, cpc: float) -> float:
        """Calculate opportunity score for a keyword"""
        # Position factor (closer to page 1 = higher opportunity)
        position_factor = max(0, (20 - position) / 20)
        
        # Volume factor (higher volume = higher opportunity)
        volume_factor = min(1.0, volume / 10000)
        
        # Difficulty factor (lower difficulty = higher opportunity)
        difficulty_factor = max(0, (100 - difficulty) / 100)
        
        # CPC factor (higher CPC = higher opportunity)
        cpc_factor = min(1.0, cpc / 5.0)
        
        # Weighted combination
        score = (
            position_factor * 0.4 +
            volume_factor * 0.3 +
            difficulty_factor * 0.2 +
            cpc_factor * 0.1
        )
        
        return min(1.0, score)
    
    def _estimate_traffic_potential(self, position: int, volume: int) -> int:
        """Estimate potential traffic if keyword reaches page 1"""
        if position <= 10:
            return 0  # Already on page 1
        
        # Traffic estimation based on position
        position_traffic = {
            1: 0.3, 2: 0.15, 3: 0.1, 4: 0.07, 5: 0.05,
            6: 0.04, 7: 0.03, 8: 0.025, 9: 0.02, 10: 0.015
        }
        
        # Estimate traffic for position 5 (middle of page 1)
        estimated_ctr = position_traffic.get(5, 0.05)
        return int(volume * estimated_ctr)
    
    def _determine_priority(self, opportunity_score: float, volume: int) -> str:
        """Determine priority level for opportunity"""
        if opportunity_score > 0.8 and volume > 5000:
            return "high"
        elif opportunity_score > 0.6 and volume > 1000:
            return "medium"
        else:
            return "low"
    
    def analyze_competitive_landscape(self, competitors_data: List[Dict[str, Any]], 
                                     current_rankings: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitive landscape and gaps"""
        if not competitors_data:
            return {}
        
        # Top competitors analysis
        top_competitors = sorted(competitors_data[:10], 
                              key=lambda x: x.get('common_keywords', 0), 
                              reverse=True)
        
        # Calculate competitive metrics
        total_common_keywords = sum(comp.get('common_keywords', 0) for comp in top_competitors)
        avg_common_keywords = total_common_keywords / len(top_competitors) if top_competitors else 0
        
        # Identify competitive gaps
        current_keywords = set(current_rankings.get('keywords', {}).keys())
        competitive_gaps = []
        
        for comp in top_competitors[:5]:  # Analyze top 5 competitors
            comp_domain = comp.get('domain', '')
            common_keywords = comp.get('common_keywords', 0)
            
            if common_keywords > avg_common_keywords:
                competitive_gaps.append({
                    'domain': comp_domain,
                    'common_keywords': common_keywords,
                    'threat_level': 'high' if common_keywords > avg_common_keywords * 1.5 else 'medium'
                })
        
        return {
            'top_competitors': top_competitors,
            'average_common_keywords': avg_common_keywords,
            'competitive_gaps': competitive_gaps,
            'market_leader': top_competitors[0] if top_competitors else None
        }
    
    def calculate_visibility_score(self, rankings_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive visibility metrics"""
        if not rankings_data:
            return {'score': 0, 'breakdown': {}}
        
        # Position-based scoring
        position_scores = {
            1: 100, 2: 90, 3: 80, 4: 70, 5: 60,
            6: 50, 7: 40, 8: 30, 9: 20, 10: 10
        }
        
        total_score = 0
        page_1_count = 0
        top_3_count = 0
        
        for keyword_data in rankings_data:
            position = keyword_data.get('position', 0)
            if position > 0 and position <= 100:
                if position <= 10:
                    page_1_count += 1
                if position <= 3:
                    top_3_count += 1
                
                # Calculate score for this position
                if position <= 10:
                    score = position_scores.get(position, 0)
                else:
                    score = max(0, 10 - (position - 10) * 0.5)
                
                total_score += score
        
        # Calculate final metrics
        total_keywords = len(rankings_data)
        visibility_score = (total_score / (total_keywords * 100)) * 100 if total_keywords > 0 else 0
        
        return {
            'score': round(visibility_score, 2),
            'total_keywords': total_keywords,
            'page_1_keywords': page_1_count,
            'top_3_keywords': top_3_count,
            'page_1_percentage': round((page_1_count / total_keywords) * 100, 2) if total_keywords > 0 else 0,
            'breakdown': {
                'positions_1_3': top_3_count,
                'positions_4_10': page_1_count - top_3_count,
                'positions_11_20': sum(1 for k in rankings_data if 11 <= k.get('position', 0) <= 20),
                'positions_21_50': sum(1 for k in rankings_data if 21 <= k.get('position', 0) <= 50),
                'positions_51_100': sum(1 for k in rankings_data if 51 <= k.get('position', 0) <= 100)
            }
        }

# Initialize analyzer
analyzer = SEOInsightsAnalyzer()

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available SEO analysis resources"""
    return [
        Resource(
            uri="seo://insights/analysis",
            name="SEO Insights Analysis",
            description="Comprehensive SEO analysis including anomalies, opportunities, and competitive insights",
            mimeType="application/json"
        ),
        Resource(
            uri="seo://insights/opportunities",
            name="SEO Opportunities",
            description="High-priority SEO opportunities with scoring and recommendations",
            mimeType="application/json"
        ),
        Resource(
            uri="seo://insights/competitive",
            name="Competitive Analysis",
            description="Competitive landscape analysis and gap identification",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read SEO analysis resources"""
    if uri == "seo://insights/analysis":
        return json.dumps({
            "message": "Use the analyze_seo_insights tool to perform comprehensive SEO analysis",
            "available_tools": [
                "analyze_seo_insights",
                "detect_anomalies", 
                "analyze_opportunities",
                "competitive_analysis",
                "visibility_analysis"
            ]
        })
    elif uri == "seo://insights/opportunities":
        return json.dumps({
            "message": "Use the analyze_opportunities tool to identify SEO opportunities"
        })
    elif uri == "seo://insights/competitive":
        return json.dumps({
            "message": "Use the competitive_analysis tool to analyze competitive landscape"
        })
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls for SEO analysis"""
    
    if name == "analyze_seo_insights":
        return await analyze_seo_insights(arguments)
    elif name == "detect_anomalies":
        return await detect_anomalies(arguments)
    elif name == "analyze_opportunities":
        return await analyze_opportunities(arguments)
    elif name == "competitive_analysis":
        return await competitive_analysis(arguments)
    elif name == "visibility_analysis":
        return await visibility_analysis(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def analyze_seo_insights(arguments: dict) -> List[TextContent]:
    """Comprehensive SEO insights analysis"""
    try:
        # Parse input data
        rankings_data = arguments.get('rankings_data', [])
        competitors_data = arguments.get('competitors_data', [])
        backlinks_data = arguments.get('backlinks_data', {})
        domain = arguments.get('domain', 'unknown.com')
        market = arguments.get('market', 'global')
        
        # Convert to our data structure
        current_rankings = {'keywords': {}}
        for item in rankings_data:
            keyword = item.get('keyword')
            if keyword:
                current_rankings['keywords'][keyword] = {
                    'position': item.get('position'),
                    'volume': item.get('volume'),
                    'cpc': item.get('cpc'),
                    'difficulty': item.get('difficulty'),
                    'traffic': item.get('traffic'),
                    'prev_position': item.get('prev_pos')
                }
        
        # Perform comprehensive analysis
        results = {
            'domain': domain,
            'market': market,
            'timestamp': datetime.now().isoformat(),
            'analysis': {}
        }
        
        # 1. Visibility Analysis
        visibility = analyzer.calculate_visibility_score(rankings_data)
        results['analysis']['visibility'] = visibility
        
        # 2. Anomaly Detection
        anomalies = analyzer.detect_anomalies(current_rankings, [])  # No historical data for now
        results['analysis']['anomalies'] = [
            {
                'keyword': a.keyword,
                'current_position': a.current_position,
                'expected_position': a.expected_position,
                'severity': a.severity,
                'z_score': a.z_score,
                'change_type': a.change_type
            } for a in anomalies
        ]
        
        # 3. Opportunity Analysis
        opportunities = analyzer.analyze_opportunities(rankings_data, competitors_data)
        results['analysis']['opportunities'] = [
            {
                'keyword': o.keyword,
                'current_position': o.current_position,
                'search_volume': o.search_volume,
                'difficulty': o.difficulty,
                'opportunity_score': o.opportunity_score,
                'potential_traffic': o.potential_traffic,
                'priority': o.priority
            } for o in opportunities
        ]
        
        # 4. Competitive Analysis
        competitive = analyzer.analyze_competitive_landscape(competitors_data, current_rankings)
        results['analysis']['competitive'] = competitive
        
        # 5. Generate Summary Report
        summary = generate_summary_report(results)
        results['summary'] = summary
        
        return [TextContent(type="text", text=json.dumps(results, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error in SEO analysis: {str(e)}")]

async def detect_anomalies(arguments: dict) -> List[TextContent]:
    """Detect ranking anomalies"""
    try:
        rankings_data = arguments.get('rankings_data', [])
        historical_data = arguments.get('historical_data', [])
        
        current_rankings = {'keywords': {}}
        for item in rankings_data:
            keyword = item.get('keyword')
            if keyword:
                current_rankings['keywords'][keyword] = {
                    'position': item.get('position'),
                    'volume': item.get('volume')
                }
        
        anomalies = analyzer.detect_anomalies(current_rankings, historical_data)
        
        result = {
            'anomalies': [
                {
                    'keyword': a.keyword,
                    'current_position': a.current_position,
                    'expected_position': a.expected_position,
                    'severity': a.severity,
                    'z_score': a.z_score,
                    'change_type': a.change_type
                } for a in anomalies
            ],
            'total_anomalies': len(anomalies),
            'high_severity': len([a for a in anomalies if a.severity == 'high'])
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error in anomaly detection: {str(e)}")]

async def analyze_opportunities(arguments: dict) -> List[TextContent]:
    """Analyze SEO opportunities"""
    try:
        rankings_data = arguments.get('rankings_data', [])
        competitors_data = arguments.get('competitors_data', [])
        
        opportunities = analyzer.analyze_opportunities(rankings_data, competitors_data)
        
        result = {
            'opportunities': [
                {
                    'keyword': o.keyword,
                    'current_position': o.current_position,
                    'search_volume': o.search_volume,
                    'difficulty': o.difficulty,
                    'opportunity_score': o.opportunity_score,
                    'potential_traffic': o.potential_traffic,
                    'priority': o.priority
                } for o in opportunities
            ],
            'total_opportunities': len(opportunities),
            'high_priority': len([o for o in opportunities if o.priority == 'high'])
        }
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error in opportunity analysis: {str(e)}")]

async def competitive_analysis(arguments: dict) -> List[TextContent]:
    """Analyze competitive landscape"""
    try:
        competitors_data = arguments.get('competitors_data', [])
        current_rankings = arguments.get('current_rankings', {})
        
        competitive = analyzer.analyze_competitive_landscape(competitors_data, current_rankings)
        
        return [TextContent(type="text", text=json.dumps(competitive, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error in competitive analysis: {str(e)}")]

async def visibility_analysis(arguments: dict) -> List[TextContent]:
    """Analyze visibility metrics"""
    try:
        rankings_data = arguments.get('rankings_data', [])
        
        visibility = analyzer.calculate_visibility_score(rankings_data)
        
        return [TextContent(type="text", text=json.dumps(visibility, indent=2))]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error in visibility analysis: {str(e)}")]

def generate_summary_report(results: dict) -> dict:
    """Generate a summary report of the analysis"""
    analysis = results.get('analysis', {})
    
    visibility = analysis.get('visibility', {})
    anomalies = analysis.get('anomalies', [])
    opportunities = analysis.get('opportunities', [])
    competitive = analysis.get('competitive', {})
    
    summary = {
        'overview': {
            'domain': results.get('domain'),
            'total_keywords': visibility.get('total_keywords', 0),
            'visibility_score': visibility.get('score', 0),
            'page_1_keywords': visibility.get('page_1_keywords', 0),
            'anomalies_detected': len(anomalies),
            'opportunities_found': len(opportunities),
            'high_priority_opportunities': len([o for o in opportunities if o.get('priority') == 'high'])
        },
        'key_insights': [],
        'recommendations': []
    }
    
    # Generate key insights
    if visibility.get('score', 0) > 70:
        summary['key_insights'].append("Strong visibility performance with high search engine presence")
    elif visibility.get('score', 0) > 40:
        summary['key_insights'].append("Moderate visibility with room for improvement")
    else:
        summary['key_insights'].append("Low visibility - significant SEO improvements needed")
    
    if len(anomalies) > 0:
        high_severity = len([a for a in anomalies if a.get('severity') == 'high'])
        if high_severity > 0:
            summary['key_insights'].append(f"{high_severity} high-severity ranking anomalies detected")
    
    if len(opportunities) > 0:
        high_priority = len([o for o in opportunities if o.get('priority') == 'high'])
        if high_priority > 0:
            summary['key_insights'].append(f"{high_priority} high-priority SEO opportunities identified")
    
    # Generate recommendations
    if visibility.get('page_1_keywords', 0) < 5:
        summary['recommendations'].append("Focus on improving rankings for existing keywords to reach page 1")
    
    if len(opportunities) > 0:
        summary['recommendations'].append("Prioritize high-opportunity keywords for content and optimization")
    
    if len(anomalies) > 0:
        summary['recommendations'].append("Investigate and address ranking anomalies to maintain stability")
    
    return summary

# Register tools
@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available SEO analysis tools"""
    return [
        Tool(
            name="analyze_seo_insights",
            description="Comprehensive SEO insights analysis including anomalies, opportunities, and competitive analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "rankings_data": {
                        "type": "array",
                        "description": "Current keyword rankings data",
                        "items": {
                            "type": "object",
                            "properties": {
                                "keyword": {"type": "string"},
                                "position": {"type": "integer"},
                                "volume": {"type": "integer"},
                                "cpc": {"type": "number"},
                                "difficulty": {"type": "integer"},
                                "traffic": {"type": "integer"},
                                "prev_pos": {"type": "integer"}
                            }
                        }
                    },
                    "competitors_data": {
                        "type": "array",
                        "description": "Competitor analysis data",
                        "items": {
                            "type": "object",
                            "properties": {
                                "domain": {"type": "string"},
                                "common_keywords": {"type": "integer"}
                            }
                        }
                    },
                    "backlinks_data": {
                        "type": "object",
                        "description": "Backlink analysis data"
                    },
                    "domain": {"type": "string", "description": "Domain being analyzed"},
                    "market": {"type": "string", "description": "Target market/region"}
                },
                "required": ["rankings_data", "domain"]
            }
        ),
        Tool(
            name="detect_anomalies",
            description="Detect ranking anomalies using statistical analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "rankings_data": {"type": "array", "description": "Current rankings data"},
                    "historical_data": {"type": "array", "description": "Historical rankings data"}
                },
                "required": ["rankings_data"]
            }
        ),
        Tool(
            name="analyze_opportunities",
            description="Identify high-priority SEO opportunities",
            inputSchema={
                "type": "object",
                "properties": {
                    "rankings_data": {"type": "array", "description": "Current rankings data"},
                    "competitors_data": {"type": "array", "description": "Competitor data"}
                },
                "required": ["rankings_data"]
            }
        ),
        Tool(
            name="competitive_analysis",
            description="Analyze competitive landscape and identify gaps",
            inputSchema={
                "type": "object",
                "properties": {
                    "competitors_data": {"type": "array", "description": "Competitor data"},
                    "current_rankings": {"type": "object", "description": "Current rankings"}
                },
                "required": ["competitors_data"]
            }
        ),
        Tool(
            name="visibility_analysis",
            description="Calculate visibility metrics and performance scores",
            inputSchema={
                "type": "object",
                "properties": {
                    "rankings_data": {"type": "array", "description": "Current rankings data"}
                },
                "required": ["rankings_data"]
            }
        )
    ]

if __name__ == "__main__":
    # Run the MCP server
    import asyncio
    asyncio.run(stdio_server(server))
