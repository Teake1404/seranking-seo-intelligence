"""
SEranking MCP Server for SEO Intelligence
Handles keyword ranking data collection and competitor analysis
"""
import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional
import aiohttp
import requests

import config

logger = logging.getLogger(__name__)

# Rate limiting for SEranking API (10 RPS = 0.1 seconds between requests)
# SEranking Data API limit: 10 requests per second
# Strategy: Wait minimum 100ms between requests + handle 429 responses with retry
_last_request_time = 0
_min_request_interval = 0.1  # 100ms between requests
_rate_limit_lock = None  # Will be initialized lazily when needed

async def make_seranking_request(endpoint: str, params: Dict[str, Any] = None, method: str = "GET") -> Dict[str, Any]:
    """
    Make authenticated request to SEranking API with rate limiting (thread-safe)
    
    Rate limiting strategy:
    1. Lock only protects timestamp read/write (critical section)
    2. Sleep happens OUTSIDE lock to allow parallel polling
    3. Ensures 10 RPS limit even with parallel execution
    """
    global _last_request_time, _rate_limit_lock
    
    # Initialize lock lazily (can't create Lock at module level)
    if _rate_limit_lock is None:
        _rate_limit_lock = asyncio.Lock()
    
    # Calculate sleep time (protected by lock)
    async with _rate_limit_lock:
        current_time = time.time()
        time_since_last = current_time - _last_request_time
        
        if time_since_last < _min_request_interval:
            sleep_time = _min_request_interval - time_since_last
        else:
            sleep_time = 0
        
        # Reserve this time slot by updating immediately
        _last_request_time = time.time() + sleep_time
    
    # Sleep OUTSIDE lock to allow other requests to calculate their wait time
    if sleep_time > 0:
        logger.info(f"Rate limiting: sleeping {sleep_time:.3f}s to respect 10 RPS limit")
        await asyncio.sleep(sleep_time)
    
    headers = {
        "Authorization": f"Token {config.SERANKING_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # SEranking uses /v1/ prefix
    url = f"https://api.seranking.com/v1{endpoint}"
    
    async with aiohttp.ClientSession() as session:
        if method == "GET":
            async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status in [200, 201]:
                    return await response.json()
                elif response.status == 429:  # Rate limit exceeded
                    error_text = await response.text()
                    logger.warning(f"Rate limit exceeded (429), retrying after delay...")
                    await asyncio.sleep(1)  # Wait 1 second and retry
                    return await make_seranking_request(endpoint, params, method)
                else:
                    error_text = await response.text()
                    raise Exception(f"SEranking API error {response.status}: {error_text}")
        else:  # POST
            async with session.post(url, json=params, headers=headers, timeout=aiohttp.ClientTimeout(total=300)) as response:
                if response.status in [200, 201]:
                    return await response.json()
                elif response.status == 429:  # Rate limit exceeded
                    error_text = await response.text()
                    logger.warning(f"Rate limit exceeded (429), retrying after delay...")
                    await asyncio.sleep(1)  # Wait 1 second and retry
                    return await make_seranking_request(endpoint, params, method)
                else:
                    error_text = await response.text()
                    raise Exception(f"SEranking API error {response.status}: {error_text}")

async def get_keyword_rankings(keywords: Optional[List[str]] = None, domain: Optional[str] = None) -> str:
    """
    Fetches current keyword rankings for a domain using SEranking SERP API
    
    Args:
        keywords: List of keywords to check. If None, uses generic keywords
        domain: Target domain to check rankings for. If None, uses config default
    
    Returns:
        JSON string containing ranking data for each keyword
    """
    if keywords is None:
        keywords = config.GENERIC_KEYWORDS[:5]
    if domain is None:
        domain = config.TARGET_DOMAIN
    
    try:
        from datetime import datetime
        
        processed_data = {
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "keywords": {}
        }
        
        # Step 1: Submit SERP tasks for all keywords
        # engine_id 368 = Google UK Desktop (for bagsoflove.co.uk)
        task_payload = {
            "engine_id": 368,  # Google UK
            "query": keywords
        }
        
        tasks_response = await make_seranking_request("/serp/tasks", task_payload, "POST")
        
        # Step 2: Wait and get results for each task
        for task_info in tasks_response:
            keyword = task_info.get("query")
            task_id = task_info.get("task_id")
            
            # Poll for results (max 5 minutes)
            import asyncio
            max_attempts = 300  # 300 seconds = 5 minutes
            for attempt in range(max_attempts):
                status_response = await make_seranking_request(
                    f"/serp/tasks/status",
                    {"task_id": task_id},
                    "GET"
                )
                
                if "results" in status_response:
                    # Task completed, find domain position
                    results = status_response.get("results", [])
                    domain_position = None
                    domain_url = None
                    domain_title = None
                    
                    for result in results:
                        url = result.get("url", "").lower()
                        if domain.lower() in url:
                            domain_position = int(result.get("position", 0))
                            domain_url = result.get("url")
                            domain_title = result.get("title")
                            break
                    
                    processed_data["keywords"][keyword] = {
                        "position": domain_position,
                        "url": domain_url,
                        "title": domain_title
                    }
                    break
                elif status_response.get("status") == "processing":
                    # Wait 1 second before next check
                    await asyncio.sleep(1)
                else:
                    # Unknown status
                    processed_data["keywords"][keyword] = {
                        "position": None,
                        "url": None,
                        "title": None,
                        "error": "Unknown status"
                    }
                    break
            else:
                # Timeout after 30 attempts
                processed_data["keywords"][keyword] = {
                    "position": None,
                    "url": None,
                    "title": None,
                    "error": "Timeout waiting for SERP results"
                }
        
        return json.dumps(processed_data, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "domain": domain})

async def get_competitor_rankings(competitors: Optional[List[str]] = None, keywords: Optional[List[str]] = None) -> str:
    """
    Tracks competitor keyword rankings using SEranking
    
    Args:
        competitors: List of competitor domains
        keywords: List of keywords to check
    
    Returns:
        JSON string containing competitor ranking data
    """
    if competitors is None:
        competitors = config.COMPETITOR_DOMAINS
    if keywords is None:
        keywords = config.GENERIC_KEYWORDS[:5]
    
    try:
        from datetime import datetime
        import asyncio
        
        processed_data = {
            "competitors": {},
            "timestamp": datetime.now().isoformat(),
            "keywords": {}
        }
        
        # Initialize competitor data structure
        for competitor in competitors:
            processed_data["competitors"][competitor] = {}
        
        # Submit SERP tasks for all keywords
        task_payload = {
            "engine_id": 368,  # Google UK
            "query": keywords
        }
        
        tasks_response = await make_seranking_request("/serp/tasks", task_payload, "POST")
        
        # Get results for each task
        for task_info in tasks_response:
            keyword = task_info.get("query")
            task_id = task_info.get("task_id")
            
            keyword_data = {}
            
            # Poll for results (max 5 minutes)
            max_attempts = 300  # 300 seconds = 5 minutes
            for attempt in range(max_attempts):
                status_response = await make_seranking_request(
                    f"/serp/tasks/status",
                    {"task_id": task_id},
                    "GET"
                )
                
                if "results" in status_response:
                    results = status_response.get("results", [])
                    
                    # Find each competitor's position
                    for competitor in competitors:
                        comp_position = None
                        comp_url = None
                        comp_title = None
                        
                        for result in results:
                            url = result.get("url", "").lower()
                            if competitor.lower() in url:
                                comp_position = int(result.get("position", 0))
                                comp_url = result.get("url")
                                comp_title = result.get("title")
                                break
                        
                        keyword_data[competitor] = {
                            "position": comp_position,
                            "url": comp_url,
                            "title": comp_title
                        }
                    
                    processed_data["keywords"][keyword] = keyword_data
                    break
                elif status_response.get("status") == "processing":
                    await asyncio.sleep(1)
                else:
                    break
        
        return json.dumps(processed_data, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "competitors": competitors})

async def get_competitor_summary(domain: str, competitors: Optional[List[str]] = None) -> str:
    """
    Get competitor summary using SEranking's competitors endpoint
    Auto-discovers competitors if none provided
    
    Args:
        domain: Target domain
        competitors: Optional list of competitor domains
    
    Returns:
        JSON string with competitor data
    """
    try:
        from datetime import datetime
        
        # If no competitors provided AND domain is set, auto-discover them
        # NOTE: Auto-discovery often finds generic sites (Amazon, eBay) not true business competitors
        # Manual competitor lists are usually more accurate for niche businesses
        if not competitors or len(competitors) == 0:
            logger.info("⚠️  Auto-discovering competitors (may include generic sites)...")
            # Use SEranking's competitor discovery endpoint
            params = {
                'source': 'uk',
                'domain': domain,
                'type': 'organic',
                'stats': '1'  # Include statistics
            }
            
            result = await make_seranking_request("/domain/competitors", params, "GET")
            
            # Take top 5 discovered competitors
            discovered = result[:5] if isinstance(result, list) else []
            
            competitor_data = {
                "timestamp": datetime.now().isoformat(),
                "auto_discovered": True,
                "competitors": []
            }
            
            for comp in discovered:
                competitor_data["competitors"].append({
                    "domain": comp.get("domain"),
                    "common_keywords": comp.get("common_keywords", 0),
                    "total_keywords": comp.get("total_keywords", 0),
                    "traffic_sum": comp.get("traffic_sum", 0),
                    "price_sum": comp.get("price_sum", 0)
                })
        else:
            # Get stats for provided competitors
            competitor_data = {
                "timestamp": datetime.now().isoformat(),
                "auto_discovered": False,
                "competitors": []
            }
            
            # For now, return basic structure
            # Would need individual domain stats calls for full data
            for comp in competitors:
                competitor_data["competitors"].append({
                    "domain": comp,
                    "common_keywords": 0,
                    "total_keywords": 0,
                    "traffic_sum": 0,
                    "price_sum": 0
                })
        
        return json.dumps(competitor_data, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "domain": domain})

async def get_backlink_changes(domain: str = None) -> str:
    """
    Monitors backlink data using SEranking
    
    Args:
        domain: Domain to check backlinks for
    
    Returns:
        JSON string containing backlink analysis data
    """
    if domain is None:
        domain = config.NIKE_DOMAIN
    
    try:
        processed_data = {
            "domain": domain,
            "timestamp": "",
            "overview": {},
            "top_referring_domains": []
        }
        
        # SEranking backlink API call here
        # Adjust based on their documentation
        
        return json.dumps(processed_data, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "domain": domain})

async def get_keyword_metrics(keywords: Optional[List[str]] = None) -> str:
    """
    Gets keyword difficulty and search volume metrics from SEranking
    
    Args:
        keywords: List of keywords to analyze
    
    Returns:
        JSON string containing keyword metrics data
    """
    if keywords is None:
        keywords = config.GENERIC_KEYWORDS[:10]
    
    try:
        from datetime import datetime
        
        processed_data = {
            "timestamp": datetime.now().isoformat(),
            "keywords": {}
        }
        
        # Use SEranking Keyword Research API
        # Note: This is a POST request with form-data
        headers = {
            "Authorization": f"Token {config.SERANKING_API_KEY}"
        }
        
        url = "https://api.seranking.com/v1/keywords/export?source=uk"  # UK for bagsoflove.co.uk
        
        # Use requests library (synchronous) - works with multipart/form-data
        # Build files list for multipart/form-data (like curl --form)
        # Use list of tuples to allow duplicate keys (keywords[])
        files = []
        for keyword in keywords:
            files.append(('keywords[]', (None, keyword)))
        files.append(('sort', (None, 'volume')))
        files.append(('sort_order', (None, 'desc')))
        
        # Make synchronous request (we're already in async context, but requests is sync)
        import concurrent.futures
        loop = asyncio.get_event_loop()
        
        def make_request():
            # Rate limiting for synchronous requests too
            current_time = time.time()
            time_since_last = current_time - _last_request_time
            if time_since_last < _min_request_interval:
                sleep_time = _min_request_interval - time_since_last
                logger.info(f"Rate limiting (sync): sleeping {sleep_time:.3f}s to respect 10 RPS limit")
                time.sleep(sleep_time)
            
            response = requests.post(url, headers=headers, files=files, timeout=300)
            return response
        
        with concurrent.futures.ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(pool, make_request)
        
        if response.status_code in [200, 201]:
            try:
                results = response.json()
                
                # Process results
                for result in results:
                    if result.get("is_data_found"):
                        keyword = result.get("keyword")
                        processed_data["keywords"][keyword] = {
                            "search_volume": result.get("volume", 0),
                            "competition": str(result.get("competition", "")),
                            "competition_index": int(float(result.get("competition", 0)) * 100),
                            "cpc": float(result.get("cpc", 0)),
                            "difficulty": result.get("difficulty", 0)
                        }
            except json.JSONDecodeError as e:
                raise Exception(f"JSON decode error: {e}, Response: {response.text}")
        else:
            raise Exception(f"SEranking API error {response.status_code}: {response.text}")
        
        return json.dumps(processed_data, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e), "keywords": keywords})

if __name__ == "__main__":
    print("SEranking MCP Server")
    print("=" * 80)
    print("This module provides SEranking API integration.")
    print()
    print("To use:")
    print("1. Sign up for SEranking trial: https://seranking.com")
    print("2. Get your API key from account settings")
    print("3. Set SERANKING_API_KEY in config.py or environment")
    print()
    print("Functions available:")
    print("  - get_nike_keyword_rankings()")
    print("  - get_competitor_rankings()")
    print("  - get_backlink_changes()")
    print("  - get_keyword_metrics()")
    print()
    print("Note: You need to adjust API calls based on SEranking documentation")
    print("      at https://seranking.com/api-documentation.html")

