"""
Redis Cache Utility for SEranking API
Provides intelligent caching with TTL and key management for SEO data
"""
import json
import logging
import hashlib
import redis
from typing import Any, Dict, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RedisCache:
    """
    Redis cache manager for SEranking API calls
    - Intelligent TTL based on data type
    - Key versioning for cache invalidation
    - Fallback to no-cache if Redis unavailable
    """
    
    def __init__(self, redis_url: str = None, enabled: bool = True):
        """
        Initialize Redis cache
        
        Args:
            redis_url: Redis connection URL (default: localhost:6379)
            enabled: Whether caching is enabled (default: True)
        """
        self.enabled = enabled
        self.redis_client = None
        self.cache_version = "v1.0"  # For cache invalidation
        
        if not enabled:
            logger.info("🚫 Redis caching disabled")
            return
            
        try:
            # Default Redis URL if not provided
            if not redis_url:
                redis_url = "redis://localhost:6379/0"
            
            # Parse Redis URL and create connection
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Redis cache connected: {redis_url}")
            
        except Exception as e:
            logger.warning(f"⚠️ Redis cache unavailable: {e}")
            logger.info("🔄 Falling back to no-cache mode")
            self.enabled = False
            self.redis_client = None
    
    def _generate_cache_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """
        Generate consistent cache key from parameters
        
        Args:
            prefix: Cache key prefix (e.g., 'rankings', 'metrics')
            params: Parameters to hash
            
        Returns:
            Cache key string
        """
        # Sort params for consistent hashing
        sorted_params = sorted(params.items())
        param_string = json.dumps(sorted_params, sort_keys=True)
        
        # Create hash of parameters
        param_hash = hashlib.md5(param_string.encode()).hexdigest()[:12]
        
        return f"seo:{self.cache_version}:{prefix}:{param_hash}"
    
    def _get_ttl(self, data_type: str) -> int:
        """
        Get TTL (Time To Live) in seconds based on data type
        
        Args:
            data_type: Type of data being cached
            
        Returns:
            TTL in seconds
        """
        ttl_map = {
            'rankings': 3600,      # 1 hour - rankings change frequently
            'competitor_rankings': 3600,  # 1 hour - competitor data
            'keyword_metrics': 86400,     # 24 hours - metrics are stable
            'competitor_summary': 86400,  # 24 hours - competitor summaries
            'backlinks': 43200,           # 12 hours - backlinks change slowly
            'default': 1800               # 30 minutes - default fallback
        }
        
        return ttl_map.get(data_type, ttl_map['default'])
    
    async def get(self, data_type: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get cached data
        
        Args:
            data_type: Type of data (e.g., 'rankings', 'metrics')
            params: Parameters used to generate the data
            
        Returns:
            Cached data or None if not found/expired
        """
        if not self.enabled or not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(data_type, params)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                logger.info(f"🎯 Cache HIT: {data_type} (key: {cache_key[:20]}...)")
                return data
            else:
                logger.info(f"❌ Cache MISS: {data_type} (key: {cache_key[:20]}...)")
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Cache get error: {e}")
            return None
    
    async def set(self, data_type: str, params: Dict[str, Any], data: Dict[str, Any]) -> bool:
        """
        Cache data with appropriate TTL
        
        Args:
            data_type: Type of data being cached
            params: Parameters used to generate the data
            data: Data to cache
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(data_type, params)
            ttl = self._get_ttl(data_type)
            
            # Add metadata to cached data
            cache_data = {
                'data': data,
                'cached_at': datetime.now().isoformat(),
                'data_type': data_type,
                'ttl': ttl
            }
            
            # Store with TTL
            self.redis_client.setex(
                cache_key, 
                ttl, 
                json.dumps(cache_data, default=str)
            )
            
            logger.info(f"💾 Cached: {data_type} (TTL: {ttl}s, key: {cache_key[:20]}...)")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Cache set error: {e}")
            return False
    
    async def invalidate(self, data_type: str = None, pattern: str = None) -> int:
        """
        Invalidate cache entries
        
        Args:
            data_type: Invalidate specific data type
            pattern: Custom pattern to match keys
            
        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.redis_client:
            return 0
        
        try:
            if pattern:
                search_pattern = pattern
            elif data_type:
                search_pattern = f"seo:{self.cache_version}:{data_type}:*"
            else:
                search_pattern = f"seo:{self.cache_version}:*"
            
            # Find matching keys
            keys = self.redis_client.keys(search_pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"🗑️ Invalidated {deleted} cache entries: {search_pattern}")
                return deleted
            else:
                logger.info(f"ℹ️ No cache entries found: {search_pattern}")
                return 0
                
        except Exception as e:
            logger.warning(f"⚠️ Cache invalidation error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        if not self.enabled or not self.redis_client:
            return {"enabled": False, "error": "Redis not available"}
        
        try:
            # Get all SEO cache keys
            keys = self.redis_client.keys(f"seo:{self.cache_version}:*")
            
            stats = {
                "enabled": True,
                "total_keys": len(keys),
                "cache_version": self.cache_version,
                "data_types": {}
            }
            
            # Count by data type
            for key in keys:
                parts = key.split(':')
                if len(parts) >= 3:
                    data_type = parts[2]
                    stats["data_types"][data_type] = stats["data_types"].get(data_type, 0) + 1
            
            return stats
            
        except Exception as e:
            return {"enabled": True, "error": str(e)}
    
    def is_available(self) -> bool:
        """Check if Redis cache is available"""
        return self.enabled and self.redis_client is not None

# Global cache instance
_cache_instance = None

def get_cache() -> RedisCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance

def cache_keyword_rankings(keywords: list, domain: str, data: dict) -> bool:
    """Cache keyword rankings data"""
    cache = get_cache()
    params = {"keywords": sorted(keywords), "domain": domain}
    return cache.set("rankings", params, data)

def cache_competitor_rankings(competitors: list, keywords: list, data: dict) -> bool:
    """Cache competitor rankings data"""
    cache = get_cache()
    params = {"competitors": sorted(competitors), "keywords": sorted(keywords)}
    return cache.set("competitor_rankings", params, data)

def cache_keyword_metrics(keywords: list, data: dict) -> bool:
    """Cache keyword metrics data"""
    cache = get_cache()
    params = {"keywords": sorted(keywords)}
    return cache.set("keyword_metrics", params, data)

def cache_competitor_summary(domain: str, competitors: list, data: dict) -> bool:
    """Cache competitor summary data"""
    cache = get_cache()
    params = {"domain": domain, "competitors": sorted(competitors)}
    return cache.set("competitor_summary", params, data)

async def get_cached_keyword_rankings(keywords: list, domain: str) -> Optional[dict]:
    """Get cached keyword rankings"""
    cache = get_cache()
    params = {"keywords": sorted(keywords), "domain": domain}
    return await cache.get("rankings", params)

async def get_cached_competitor_rankings(competitors: list, keywords: list) -> Optional[dict]:
    """Get cached competitor rankings"""
    cache = get_cache()
    params = {"competitors": sorted(competitors), "keywords": sorted(keywords)}
    return await cache.get("competitor_rankings", params)

async def get_cached_keyword_metrics(keywords: list) -> Optional[dict]:
    """Get cached keyword metrics"""
    cache = get_cache()
    params = {"keywords": sorted(keywords)}
    return await cache.get("keyword_metrics", params)

async def get_cached_competitor_summary(domain: str, competitors: list) -> Optional[dict]:
    """Get cached competitor summary"""
    cache = get_cache()
    params = {"domain": domain, "competitors": sorted(competitors)}
    return await cache.get("competitor_summary", params)


