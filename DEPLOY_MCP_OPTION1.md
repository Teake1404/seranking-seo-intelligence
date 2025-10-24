# 🚀 Option 1: Separate MCP Server Deployment

## 📋 **Deployment Commands for Google Cloud Shell:**

### **Step 1: Deploy SEranking MCP Server**

```bash
# Create MCP server directory
mkdir seo-mcp-server
cd seo-mcp-server

# Copy MCP server Dockerfile
cp ../Dockerfile.mcp-server ./Dockerfile

# Deploy MCP server
gcloud run deploy seranking-mcp-server \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 3000 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 900 \
  --max-instances 5

# Get MCP server URL
MCP_URL=$(gcloud run services describe seranking-mcp-server \
  --region us-central1 \
  --format="value(status.url)")

echo "MCP Server URL: $MCP_URL"
```

### **Step 2: Deploy Enhanced SEO API**

```bash
# Go back to main directory
cd ..

# Copy API Dockerfile
cp Dockerfile.api ./Dockerfile

# Deploy Enhanced SEO API
gcloud run deploy seranking-seo-api-enhanced \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10 \
  --set-env-vars="MCP_SERVER_URL=$MCP_URL,SERANKING_API_KEY=b931695c-9e38-cde4-4d4b-49eeb217118f,ANTHROPIC_API_KEY=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"

# Get API URL
API_URL=$(gcloud run services describe seranking-seo-api-enhanced \
  --region us-central1 \
  --format="value(status.url)")

echo "Enhanced SEO API URL: $API_URL"
```

### **Step 3: Test the Deployment**

```bash
# Test MCP server
curl $MCP_URL/health

# Test Enhanced SEO API
curl $API_URL/health

# Test with Bags of Love
curl -X POST $API_URL/api/enhanced-report \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "bagsoflove.co.uk",
    "market": "uk", 
    "keywords": ["personalized gifts", "photo blankets", "photo mugs", "photo puzzles"],
    "competitors": ["notonthehighstreet.com", "moonpig.com", "gettingpersonal.co.uk"]
  }'
```

## 🎯 **Architecture:**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   n8n Workflow  │───▶│  Enhanced API   │───▶│  MCP Server     │
│                 │    │  (Cloud Run)    │    │  (Cloud Run)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Claude AI      │    │  SEranking API  │
                       │  (Anthropic)    │    │  (Official)     │
                       └─────────────────┘    └─────────────────┘
```

## ✅ **Benefits:**

- ✅ **Fast MCP data fetching** - Official SEranking MCP
- ✅ **Scalable** - Separate services can scale independently  
- ✅ **Reliable** - MCP server handles rate limits efficiently
- ✅ **Maintainable** - Clear separation of concerns
- ✅ **Professional** - Uses official SEranking infrastructure

## 🚀 **Ready to Deploy!**

Just run the commands above in your Google Cloud Shell to get your enhanced SEO Intelligence API with fast MCP data fetching!
