"""
DataForSEO MCP Server for Nike SEO Intelligence
Handles keyword ranking data collection and competitor analysis
"""
import asyncio
import json
import base64
from typing import Dict, List, Any, Optional
import aiohttp

# MCP imports not needed for API usage
# try:
#     from mcp.server import Server
#     from mcp.types import Tool, TextContent
# except ImportError:
#     from mcp_stub import Server, Tool, TextContent

import config

# MCP Server - not needed for API usage
# mcp = Server("dataforseo-mcp")

def create_auth_header() -> str:
    """Create DataForSEO API authentication header"""
    credentials = f"{config.DATAFORSEO_LOGIN}:{config.DATAFORSEO_PASSWORD}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded_credentials}"

async def make_dataforseo_request(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Make authenticated request to DataForSEO API"""
    headers = {
        "Authorization": create_auth_header(),
        "Content-Type": "application/json"
    }
    
    url = f"{config.DATAFORSEO_API_BASE}{endpoint}"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers, timeout=config.REQUEST_TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"DataForSEO API error {response.status}: {error_text}")

# @mcp.tool()  # Not needed for API usage
async def get_nike_keyword_rankings(keywords: Optional[List[str]] = None) -> str:
    """
    Fetches current keyword rankings for Nike.com
    
    Args:
        keywords: List of keywords to check. If None, uses generic keywords (non-branded)
    
    Returns:
        JSON string containing ranking data for each keyword
    """
    if keywords is None:
        keywords = config.GENERIC_KEYWORDS[:5]  # Limit to 5 for API efficiency
    
    # Prepare payload for DataForSEO SERP API
    payload = []
    
    for keyword in keywords:
        task = {
            "keyword": keyword,
            "language_code": "en",
            "location_code": 2840,  # United States
            "device": "desktop",
            "os": "windows",
            "depth": 100  # Get top 100 results
        }
        payload.append(task)
    
    try:
        result = await make_dataforseo_request("/serp/google/organic/live/advanced", payload)
        
        # Process results to extract Nike.com rankings
        processed_data = {
            "domain": config.NIKE_DOMAIN,
            "timestamp": result.get("datetime", ""),
            "keywords": {}
        }
        
        for task_result in result.get("tasks", []):
            result_items = task_result.get("result", [])
            if not result_items:
                continue
            keyword = result_items[0].get("keyword", "")
            organic_results = result_items[0].get("items", [])
            
            nike_position = None
            for idx, item in enumerate(organic_results, 1):
                if item.get("type") == "organic":
                    domain = item.get("domain", "").lower()
                    if config.NIKE_DOMAIN in domain:
                        nike_position = idx
                        break
            
            processed_data["keywords"][keyword] = {
                "position": nike_position,
                "url": next((item.get("url") for item in organic_results if config.NIKE_DOMAIN in item.get("domain", "").lower()), None),
                "title": next((item.get("title") for item in organic_results if config.NIKE_DOMAIN in item.get("domain", "").lower()), None)
            }
        
        return json.dumps(processed_data, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "domain": config.NIKE_DOMAIN})

# @mcp.tool()  # Not needed for API usage
async def get_competitor_rankings(competitors: Optional[List[str]] = None, keywords: Optional[List[str]] = None) -> str:
    """
    Tracks competitor keyword rankings for the same keywords
    
    Args:
        competitors: List of competitor domains. If None, uses default from config
        keywords: List of keywords to check. If None, uses default Nike keywords
    
    Returns:
        JSON string containing competitor ranking data
    """
    if competitors is None:
        competitors = config.COMPETITOR_DOMAINS
    if keywords is None:
        keywords = config.GENERIC_KEYWORDS[:5]  # Limit to 5 for API efficiency
    
    payload = []
    
    for keyword in keywords:
        task = {
            "keyword": keyword,
            "language_code": "en", 
            "location_code": 2840,
            "device": "desktop",
            "os": "windows",
            "depth": 100
        }
        payload.append(task)
    
    try:
        result = await make_dataforseo_request("/serp/google/organic/live/advanced", payload)
        
        processed_data = {
            "competitors": {},
            "timestamp": result.get("datetime", ""),
            "keywords": {}
        }
        
        # Initialize competitor data structure
        for competitor in competitors:
            processed_data["competitors"][competitor] = {}
        
        for task_result in result.get("tasks", []):
            result_items = task_result.get("result", [])
            if not result_items:
                continue
            keyword = result_items[0].get("keyword", "")
            organic_results = result_items[0].get("items", [])
            
            keyword_data = {}
            
            for competitor in competitors:
                competitor_position = None
                competitor_url = None
                competitor_title = None
                
                for idx, item in enumerate(organic_results, 1):
                    if item.get("type") == "organic":
                        domain = item.get("domain", "").lower()
                        if competitor.lower() in domain:
                            competitor_position = idx
                            competitor_url = item.get("url")
                            competitor_title = item.get("title")
                            break
                
                keyword_data[competitor] = {
                    "position": competitor_position,
                    "url": competitor_url,
                    "title": competitor_title
                }
            
            processed_data["keywords"][keyword] = keyword_data
        
        return json.dumps(processed_data, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "competitors": competitors})

# @mcp.tool()  # Not needed for API usage
async def get_backlink_changes(domain: str = None) -> str:
    """
    Monitors backlink gains/losses for Nike.com
    
    Args:
        domain: Domain to check backlinks for. Defaults to Nike.com
    
    Returns:
        JSON string containing backlink analysis data
    """
    if domain is None:
        domain = config.NIKE_DOMAIN
    
    # Get backlinks overview
    payload = {
        "target": domain,
        "limit": 1000,
        "backlinks_status_type": "all",
        "include_subdomains": True,
        "order_by": ["rank,desc"]
    }
    
    try:
        # Get current backlinks
        result = await make_dataforseo_request("/backlinks/overview/live", [payload])
        
        processed_data = {
            "domain": domain,
            "timestamp": result.get("datetime", ""),
            "overview": {},
            "top_referring_domains": [],
            "top_pages": []
        }
        
        if result.get("tasks") and len(result["tasks"]) > 0:
            task_data = result["tasks"][0]
            if task_data.get("result"):
                result_data = task_data["result"][0]
                
                # Overview metrics
                processed_data["overview"] = {
                    "backlinks": result_data.get("backlinks", 0),
                    "referring_domains": result_data.get("referring_domains", 0),
                    "referring_main_domains": result_data.get("referring_main_domains", 0),
                    "referring_ips": result_data.get("referring_ips", 0),
                    "referring_subnets": result_data.get("referring_subnets", 0),
                    "referring_pages": result_data.get("referring_pages", 0),
                    "dofollow": result_data.get("dofollow", 0),
                    "nofollow": result_data.get("nofollow", 0),
                    "referring_page_types": result_data.get("referring_page_types", {}),
                    "top_anchor": result_data.get("top_anchor", ""),
                    "top_page_rank": result_data.get("top_page_rank", 0)
                }
        
        # Get top referring domains
        domains_payload = {
            "target": domain,
            "limit": 50,
            "order_by": ["rank,desc"]
        }
        
        domains_result = await make_dataforseo_request("/backlinks/summary/live", [domains_payload])
        
        if domains_result.get("tasks") and len(domains_result["tasks"]) > 0:
            domains_data = domains_result["tasks"][0]
            if domains_data.get("result"):
                for domain_item in domains_data["result"]:
                    processed_data["top_referring_domains"].append({
                        "domain": domain_item.get("domain", ""),
                        "rank": domain_item.get("rank", 0),
                        "backlinks": domain_item.get("backlinks", 0),
                        "referring_pages": domain_item.get("referring_pages", 0)
                    })
        
        return json.dumps(processed_data, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "domain": domain})

# @mcp.tool()  # Not needed for API usage
async def get_keyword_metrics(keywords: Optional[List[str]] = None) -> str:
    """
    Gets keyword difficulty and search volume metrics
    
    Args:
        keywords: List of keywords to analyze
    
    Returns:
        JSON string containing keyword metrics data
    """
    if keywords is None:
        keywords = config.GENERIC_KEYWORDS[:10]  # Limit for API efficiency
    
    payload = {
        "keywords": keywords,
        "language_code": "en",
        "location_code": 2840,
        "filters": [
            ["keyword_info.search_volume", ">", 0]
        ]
    }
    
    try:
        result = await make_dataforseo_request("/keywords_data/google_ads/search_volume/live", [payload])
        
        processed_data = {
            "timestamp": result.get("datetime", ""),
            "keywords": {}
        }
        
        if result.get("tasks") and len(result["tasks"]) > 0:
            task_data = result["tasks"][0]
            if task_data.get("result"):
                for keyword_data in task_data["result"]:
                    keyword = keyword_data.get("keyword", "")
                    processed_data["keywords"][keyword] = {
                        "search_volume": keyword_data.get("search_volume", 0),
                        "competition": keyword_data.get("competition", ""),
                        "competition_index": keyword_data.get("competition_index", 0),
                        "cpc": keyword_data.get("cpc", 0),
                        "low_top_of_page_bid": keyword_data.get("low_top_of_page_bid", 0),
                        "high_top_of_page_bid": keyword_data.get("high_top_of_page_bid", 0)
                    }
        
        return json.dumps(processed_data, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "keywords": keywords})

async def main():
    """Test the DataForSEO integration"""
    print("DataForSEO Integration Module")
    print("=" * 80)
    print(f"Monitoring domain: {config.NIKE_DOMAIN}")
    print(f"Keywords configured: {len(config.GENERIC_KEYWORDS)}")
    print(f"Competitors configured: {len(config.COMPETITOR_DOMAINS)}")
    print()
    print("This module is used by the API - not run directly.")
    print("To test, use test_local.py or call the API endpoint.")

if __name__ == "__main__":
    asyncio.run(main())

