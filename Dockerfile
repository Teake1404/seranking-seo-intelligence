# Dockerfile for Google Cloud Run Deployment
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY final_api_seranking.py .
COPY enhanced_api_seranking.py .
COPY seranking_mcp.py .
COPY claude_insights.py .
COPY enhanced_claude_insights.py .
COPY seo_opportunity_analysis.py .
COPY redis_cache.py .
COPY config.py .

# Expose port for Cloud Run
EXPOSE 8080

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "300", "enhanced_api_seranking:app"]


