"""
Configuration file for SEO Intelligence MCP
"""
import os
from typing import Dict, List

# Load environment variables from .env file (for local development only)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available in production - that's OK, env vars set directly
    pass

# DataForSEO API Configuration (kept for reference)
DATAFORSEO_LOGIN = os.getenv("DATAFORSEO_LOGIN")
DATAFORSEO_PASSWORD = os.getenv("DATAFORSEO_PASSWORD")
DATAFORSEO_API_BASE = "https://api.dataforseo.com/v3"

# SEranking API Configuration (ACTIVE - using trial)
SERANKING_API_KEY = os.getenv("SERANKING_API_KEY")
SERANKING_API_BASE = "https://api4.seranking.com"

# Target Domain Configuration (defaults - can be overridden by API)
TARGET_DOMAIN = os.getenv("TARGET_DOMAIN", "bagsoflove.co.uk")

# Default keywords (can be overridden by API request)
# These are just examples - users should provide their own
GENERIC_KEYWORDS = [
    "custom t shirts",
    "custom gifts",
    "photo gifts",
    "photo blanket"
]

# Default keyword priorities (can be overridden by API request)
# Used for filtering: high = check daily, medium = weekly, low = monthly
DEFAULT_KEYWORD_PRIORITIES = {
    "custom t shirts": "high",
    "custom gifts": "high",
    "photo gifts": "medium",
    "photo blanket": "low"
}

# Default Competitor Domains (can be overridden by API request)
COMPETITOR_DOMAINS = [
    "notonthehighstreet.com",
    "moonpig.com",
    "gettingpersonal.co.uk"
]

# Flask API Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Slack Configuration (for report delivery)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")

# Anthropic Claude AI Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Latest Sonnet 4 model

# Analysis Configuration
ANOMALY_THRESHOLD = 5  # Flag position changes > 5 positions
MIN_VISIBILITY_CHANGE = 0.5  # Minimum visibility change to report

# Rate Limiting
DATAFORSEO_RATE_LIMIT = 1000  # requests per minute
REQUEST_TIMEOUT = 300  # seconds (5 minutes for SEranking SERP processing)

# Redis Cache Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_CACHE_ENABLED = os.getenv("REDIS_CACHE_ENABLED", "true").lower() == "true"
REDIS_CACHE_TTL = {
    "rankings": 3600,           # 1 hour - rankings change frequently
    "competitor_rankings": 3600, # 1 hour - competitor data
    "keyword_metrics": 86400,    # 24 hours - metrics are stable
    "competitor_summary": 86400, # 24 hours - competitor summaries
    "backlinks": 43200,         # 12 hours - backlinks change slowly
    "default": 1800             # 30 minutes - default fallback
}

# Report Configuration
REPORT_EMOJI = "📊"
REPORT_TITLE = "SEO DAILY BRIEF"

