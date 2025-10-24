# Redis Cache Implementation for SEranking API

## 🚀 Overview

Redis caching has been integrated into your SEranking API to dramatically improve performance and reduce API calls. This implementation provides intelligent caching with TTL (Time To Live) management and automatic fallback when Redis is unavailable.

## 📊 Performance Benefits

- **Faster Response Times**: Cached data returns in ~50ms vs 30-300s for fresh API calls
- **Reduced API Costs**: Fewer SEranking API calls = lower costs
- **Better Rate Limiting**: Less pressure on SEranking's 10 RPS limit
- **Improved Reliability**: Graceful fallback when Redis is unavailable

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   n8n Workflow  │───▶│  SEO API        │───▶│  Redis Cache    │
│                 │    │  (Cloud Run)    │    │  (Optional)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  SEranking API  │
                       │  (External)     │
                       └─────────────────┘
```

## ⚙️ Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0          # Redis connection URL
REDIS_CACHE_ENABLED=true                    # Enable/disable caching

# For Google Cloud Run (use Cloud Memorystore)
REDIS_URL=redis://10.x.x.x:6379/0          # Cloud Memorystore IP
```

### Cache TTL Settings

| Data Type | TTL | Reason |
|-----------|-----|--------|
| Rankings | 1 hour | Rankings change frequently |
| Competitor Rankings | 1 hour | Competitor data changes often |
| Keyword Metrics | 24 hours | Metrics are stable |
| Competitor Summary | 24 hours | Summaries change slowly |
| Backlinks | 12 hours | Backlinks change slowly |

## 🚀 Deployment Options

### Option 1: Local Development with Docker Compose

```bash
# Start Redis + API together
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f seo-api
```

### Option 2: Google Cloud Run + Cloud Memorystore

```bash
# 1. Create Cloud Memorystore Redis instance
gcloud redis instances create seo-cache \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_6_x

# 2. Get Redis IP
gcloud redis instances describe seo-cache --region=us-central1

# 3. Deploy API with Redis URL
gcloud run deploy seo-api \
    --source . \
    --set-env-vars REDIS_URL=redis://10.x.x.x:6379/0 \
    --region=us-central1
```

### Option 3: No Redis (Fallback Mode)

```bash
# Deploy without Redis - caching will be disabled
gcloud run deploy seo-api \
    --source . \
    --set-env-vars REDIS_CACHE_ENABLED=false \
    --region=us-central1
```

## 📈 Cache Management

### Check Cache Status

```bash
# Health check includes cache status
curl https://your-api-url/health

# Get detailed cache statistics
curl https://your-api-url/api/cache/stats
```

### Invalidate Cache

```bash
# Clear all cache
curl -X POST https://your-api-url/api/cache/invalidate

# Clear specific data type
curl -X POST https://your-api-url/api/cache/invalidate \
  -H "Content-Type: application/json" \
  -d '{"data_type": "rankings"}'

# Clear with custom pattern
curl -X POST https://your-api-url/api/cache/invalidate \
  -H "Content-Type: application/json" \
  -d '{"pattern": "seo:v1.0:rankings:*"}'
```

## 🔍 Cache Key Structure

```
seo:v1.0:rankings:abc123def456
seo:v1.0:competitor_rankings:def456ghi789
seo:v1.0:keyword_metrics:ghi789jkl012
seo:v1.0:competitor_summary:jkl012mno345
```

- `seo`: Project prefix
- `v1.0`: Cache version (for invalidation)
- `rankings`: Data type
- `abc123def456`: MD5 hash of parameters

## 📊 Monitoring & Logs

### Cache Hit/Miss Logs

```
🎯 Cache HIT: rankings (key: seo:v1.0:rankings:abc...)
❌ Cache MISS: rankings (key: seo:v1.0:rankings:def...)
💾 Cached: rankings (TTL: 3600s, key: seo:v1.0:rankings:ghi...)
```

### Performance Metrics

```bash
# Check cache statistics
curl https://your-api-url/api/cache/stats

# Response example:
{
  "success": true,
  "cache_stats": {
    "enabled": true,
    "total_keys": 15,
    "cache_version": "v1.0",
    "data_types": {
      "rankings": 5,
      "competitor_rankings": 3,
      "keyword_metrics": 4,
      "competitor_summary": 3
    }
  }
}
```

## 🛠️ Development

### Local Testing

```bash
# Start Redis locally
docker run -d -p 6379:6379 redis:7-alpine

# Test cache functionality
python -c "
import asyncio
from redis_cache import get_cache

async def test():
    cache = get_cache()
    print('Cache available:', cache.is_available())
    stats = await cache.get_stats()
    print('Cache stats:', stats)

asyncio.run(test())
"
```

### Cache Debugging

```bash
# Connect to Redis CLI
redis-cli

# List all SEO cache keys
KEYS seo:v1.0:*

# Get specific cache entry
GET seo:v1.0:rankings:abc123def456

# Check TTL
TTL seo:v1.0:rankings:abc123def456
```

## 🔧 Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```
   ⚠️ Redis cache unavailable: [Errno 111] Connection refused
   🔄 Falling back to no-cache mode
   ```
   - **Solution**: Check Redis is running and URL is correct

2. **Cache Not Working**
   ```
   ❌ Cache MISS: rankings (key: seo:v1.0:rankings:abc...)
   ```
   - **Solution**: Check `REDIS_CACHE_ENABLED=true` and Redis connection

3. **Memory Issues**
   ```
   Redis memory usage high
   ```
   - **Solution**: Adjust TTL values or increase Redis memory

### Performance Tuning

```python
# Adjust TTL in config.py
REDIS_CACHE_TTL = {
    "rankings": 1800,        # 30 minutes (faster updates)
    "keyword_metrics": 43200, # 12 hours (less frequent)
}
```

## 🎯 Best Practices

1. **Monitor Cache Hit Rate**: Aim for 70%+ hit rate
2. **Set Appropriate TTL**: Balance freshness vs performance
3. **Use Cache Invalidation**: Clear cache when data changes
4. **Monitor Memory Usage**: Prevent Redis OOM errors
5. **Test Fallback Mode**: Ensure API works without Redis

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with cache status |
| `/api/cache/stats` | GET | Cache statistics |
| `/api/cache/invalidate` | POST | Invalidate cache |
| `/api/generate-report` | POST | Generate report (uses cache) |

## 🚀 Next Steps

1. **Deploy with Redis**: Use Cloud Memorystore for production
2. **Monitor Performance**: Track cache hit rates and response times
3. **Optimize TTL**: Adjust based on your data update frequency
4. **Scale Redis**: Increase memory as cache grows
5. **Add Metrics**: Integrate with monitoring tools

---

**Redis caching is now fully integrated! Your SEranking API will be significantly faster and more cost-effective.** 🎉


