#!/bin/bash

# Start SEranking MCP server in background
echo "🚀 Starting SEranking MCP server..."
cd seo-data-api-mcp-server
docker compose up -d &
MCP_PID=$!

# Wait for MCP server to start
echo "⏳ Waiting for MCP server to start..."
sleep 30

# Check if MCP server is running
if docker ps | grep -q "se-ranking-seo-data-api-mcp-server"; then
    echo "✅ SEranking MCP server started successfully"
else
    echo "❌ Failed to start SEranking MCP server"
fi

# Start the enhanced API
echo "🚀 Starting Enhanced SEO Intelligence API..."
cd /app
exec gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 4 --timeout 300 enhanced_api_seranking:app
