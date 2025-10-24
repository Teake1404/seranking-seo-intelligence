"""
SEranking MCP Integration for SEO Intelligence API
Uses the official SEranking MCP server for reliable data access
"""
import asyncio
import json
import logging
import subprocess
import time
from typing import Dict, List, Any, Optional
import requests

logger = logging.getLogger(__name__)

class SErankingMCPClient:
    """
    Client for SEranking MCP server integration
    Provides a Python interface to the SEranking MCP tools
    """
    
    def __init__(self, api_token: str, mcp_server_url: str = None):
        """
        Initialize SEranking MCP client
        
        Args:
            api_token: SEranking API token
            mcp_server_url: Optional MCP server URL (for remote deployment)
        """
        self.api_token = api_token
        self.mcp_server_url = mcp_server_url
        self.base_url = mcp_server_url or "http://localhost:3000"
        
    async def call_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a specific MCP tool
        
        Args:
            tool_name: Name of the MCP tool to call
            parameters: Parameters for the tool
            
        Returns:
            Tool response data
        """
        try:
            # MCP tool call structure
            mcp_request = {
                "jsonrpc": "2.0",
                "id": int(time.time() * 1000),
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": parameters
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
            
            # Make request to MCP server
            response = requests.post(
                f"{self.base_url}/mcp",
                json=mcp_request,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    return result["result"]
                elif "error" in result:
                    raise Exception(f"MCP Error: {result['error']}")
            else:
                raise Exception(f"HTTP Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            raise
    
    async def get_domain_keywords(self, domain: str, market: str = "us") -> Dict[str, Any]:
        """
        Get keyword rankings for a domain using MCP
        
        Args:
            domain: Target domain
            market: Market (us, uk, etc.)
            
        Returns:
            Keyword ranking data
        """
        try:
            parameters = {
                "domain": domain,
                "market": market,
                "limit": 100
            }
            
            result = await self.call_mcp_tool("domainKeywords", parameters)
            return result
            
        except Exception as e:
            logger.error(f"Error getting domain keywords: {e}")
            return {"error": str(e), "keywords": []}
    
    async def get_domain_competitors(self, domain: str, market: str = "us") -> Dict[str, Any]:
        """
        Get competitor analysis for a domain using MCP
        
        Args:
            domain: Target domain
            market: Market (us, uk, etc.)
            
        Returns:
            Competitor data
        """
        try:
            parameters = {
                "domain": domain,
                "market": market,
                "limit": 20
            }
            
            result = await self.call_mcp_tool("domainCompetitors", parameters)
            return result
            
        except Exception as e:
            logger.error(f"Error getting domain competitors: {e}")
            return {"error": str(e), "competitors": []}
    
    async def get_keyword_metrics(self, keywords: List[str], market: str = "us") -> Dict[str, Any]:
        """
        Get keyword metrics using MCP
        
        Args:
            keywords: List of keywords to analyze
            market: Market (us, uk, etc.)
            
        Returns:
            Keyword metrics data
        """
        try:
            parameters = {
                "keywords": keywords,
                "market": market
            }
            
            result = await self.call_mcp_tool("keywordMetrics", parameters)
            return result
            
        except Exception as e:
            logger.error(f"Error getting keyword metrics: {e}")
            return {"error": str(e), "metrics": {}}
    
    async def get_backlinks(self, domain: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get backlink data using MCP
        
        Args:
            domain: Target domain
            limit: Number of backlinks to retrieve
            
        Returns:
            Backlink data
        """
        try:
            parameters = {
                "domain": domain,
                "limit": limit
            }
            
            result = await self.call_mcp_tool("backlinksAll", parameters)
            return result
            
        except Exception as e:
            logger.error(f"Error getting backlinks: {e}")
            return {"error": str(e), "backlinks": []}
    
    async def get_domain_overview(self, domain: str, market: str = "us") -> Dict[str, Any]:
        """
        Get comprehensive domain overview using MCP
        
        Args:
            domain: Target domain
            market: Market (us, uk, etc.)
            
        Returns:
            Domain overview data
        """
        try:
            parameters = {
                "domain": domain,
                "market": market
            }
            
            result = await self.call_mcp_tool("domainOverview", parameters)
            return result
            
        except Exception as e:
            logger.error(f"Error getting domain overview: {e}")
            return {"error": str(e), "overview": {}}

# Global MCP client instance
_mcp_client = None

def get_mcp_client() -> SErankingMCPClient:
    """Get global MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        import config
        _mcp_client = SErankingMCPClient(config.SERANKING_API_KEY)
    return _mcp_client

async def get_keyword_rankings_mcp(keywords: Optional[List[str]] = None, domain: Optional[str] = None) -> str:
    """
    Get keyword rankings using SEranking MCP
    
    Args:
        keywords: List of keywords to check
        domain: Target domain
        
    Returns:
        JSON string with ranking data
    """
    if domain is None:
        import config
        domain = config.TARGET_DOMAIN
    
    try:
        client = get_mcp_client()
        
        # Get domain keywords from MCP
        domain_data = await client.get_domain_keywords(domain, "uk")
        
        # Filter for specific keywords if provided
        if keywords:
            filtered_keywords = {}
            for keyword in keywords:
                # Look for keyword in domain data
                if "keywords" in domain_data:
                    for kw_data in domain_data["keywords"]:
                        if kw_data.get("keyword", "").lower() == keyword.lower():
                            filtered_keywords[keyword] = {
                                "position": kw_data.get("position"),
                                "url": kw_data.get("url"),
                                "title": kw_data.get("title")
                            }
                            break
                    else:
                        # Keyword not found in rankings
                        filtered_keywords[keyword] = {
                            "position": None,
                            "url": None,
                            "title": None
                        }
        else:
            # Use all keywords from domain data
            filtered_keywords = {}
            if "keywords" in domain_data:
                for kw_data in domain_data["keywords"][:10]:  # Limit to top 10
                    keyword = kw_data.get("keyword", "")
                    filtered_keywords[keyword] = {
                        "position": kw_data.get("position"),
                        "url": kw_data.get("url"),
                        "title": kw_data.get("title")
                    }
        
        # Format response
        result = {
            "domain": domain,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "keywords": filtered_keywords
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in get_keyword_rankings_mcp: {e}")
        return json.dumps({"error": str(e), "domain": domain})

async def get_competitor_rankings_mcp(competitors: Optional[List[str]] = None, keywords: Optional[List[str]] = None) -> str:
    """
    Get competitor rankings using SEranking MCP
    
    Args:
        competitors: List of competitor domains
        keywords: List of keywords to check
        
    Returns:
        JSON string with competitor data
    """
    try:
        client = get_mcp_client()
        
        # Get competitor data for each competitor
        competitor_data = {
            "competitors": {},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "keywords": {}
        }
        
        if competitors:
            for competitor in competitors:
                comp_data = await client.get_domain_keywords(competitor, "uk")
                competitor_data["competitors"][competitor] = comp_data
                
                # Extract keyword rankings
                if "keywords" in comp_data:
                    for kw_data in comp_data["keywords"]:
                        keyword = kw_data.get("keyword", "")
                        if not keywords or keyword.lower() in [k.lower() for k in keywords]:
                            if keyword not in competitor_data["keywords"]:
                                competitor_data["keywords"][keyword] = {}
                            
                            competitor_data["keywords"][keyword][competitor] = {
                                "position": kw_data.get("position"),
                                "url": kw_data.get("url"),
                                "title": kw_data.get("title")
                            }
        
        return json.dumps(competitor_data, indent=2)
        
    except Exception as e:
        logger.error(f"Error in get_competitor_rankings_mcp: {e}")
        return json.dumps({"error": str(e), "competitors": competitors or []})

async def get_keyword_metrics_mcp(keywords: Optional[List[str]] = None) -> str:
    """
    Get keyword metrics using SEranking MCP
    
    Args:
        keywords: List of keywords to analyze
        
    Returns:
        JSON string with metrics data
    """
    if keywords is None:
        import config
        keywords = config.GENERIC_KEYWORDS[:10]
    
    try:
        client = get_mcp_client()
        
        # Get keyword metrics from MCP
        metrics_data = await client.get_keyword_metrics(keywords, "uk")
        
        # Format response
        result = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "keywords": {}
        }
        
        if "metrics" in metrics_data:
            for metric in metrics_data["metrics"]:
                keyword = metric.get("keyword", "")
                result["keywords"][keyword] = {
                    "search_volume": metric.get("volume", 0),
                    "competition": metric.get("competition", "Unknown"),
                    "competition_index": metric.get("competition_index", 0),
                    "cpc": metric.get("cpc", 0),
                    "difficulty": metric.get("difficulty", 0)
                }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error in get_keyword_metrics_mcp: {e}")
        return json.dumps({"error": str(e), "keywords": keywords})

async def get_competitor_summary_mcp(domain: str, competitors: Optional[List[str]] = None) -> str:
    """
    Get competitor summary using SEranking MCP
    
    Args:
        domain: Target domain
        competitors: List of competitor domains
        
    Returns:
        JSON string with competitor summary
    """
    try:
        client = get_mcp_client()
        
        # Get domain overview
        overview = await client.get_domain_overview(domain, "uk")
        
        # Get competitor data
        competitor_summary = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "auto_discovered": False,
            "competitors": []
        }
        
        if competitors:
            for competitor in competitors:
                comp_overview = await client.get_domain_overview(competitor, "uk")
                competitor_summary["competitors"].append({
                    "domain": competitor,
                    "common_keywords": comp_overview.get("common_keywords", 0),
                    "total_keywords": comp_overview.get("total_keywords", 0),
                    "traffic_sum": comp_overview.get("traffic_sum", 0),
                    "price_sum": comp_overview.get("price_sum", 0)
                })
        
        return json.dumps(competitor_summary, indent=2)
        
    except Exception as e:
        logger.error(f"Error in get_competitor_summary_mcp: {e}")
        return json.dumps({"error": str(e), "domain": domain})

# Health check for MCP server
async def check_mcp_health() -> Dict[str, Any]:
    """
    Check if MCP server is healthy
    
    Returns:
        Health status
    """
    try:
        client = get_mcp_client()
        
        # Try to get a simple domain overview
        result = await client.get_domain_overview("example.com", "us")
        
        return {
            "status": "healthy",
            "mcp_server": "connected",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "mcp_server": "disconnected",
            "error": str(e),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
        }

