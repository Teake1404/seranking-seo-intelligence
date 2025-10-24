# 🚀 Google Cloud Deployment Guide

## 📋 **Prerequisites:**

1. **Google Cloud Project ID**: `titanium-gadget-451710-i7`
2. **GitHub Repository**: Create a new private repository
3. **Google Cloud CLI**: Installed and authenticated
4. **Docker**: Installed and running

## 🔧 **Step 1: Initialize Git Repository**

```bash
# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Enhanced SEO Intelligence API with opportunity analysis"

# Add remote origin (replace with your GitHub repo URL)
git remote add origin https://github.com/yourusername/enhanced-seo-intelligence-api.git

# Push to GitHub
git push -u origin main
```

## 🚀 **Step 2: Deploy to Google Cloud Run**

### **Set Project ID:**
```bash
# Set your Google Cloud project
gcloud config set project titanium-gadget-451710-i7

# Verify project is set
gcloud config get-value project
```

### **Deploy Enhanced API:**
```bash
# Deploy the enhanced SEO Intelligence API
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
  --project titanium-gadget-451710-i7
```

### **Set Environment Variables:**
```bash
# Set your API keys
gcloud run services update seranking-seo-api-enhanced \
  --region us-central1 \
  --project titanium-gadget-451710-i7 \
  --set-env-vars="SERANKING_API_KEY=b931695c-9e38-cde4-4d4b-49eeb217118f,ANTHROPIC_API_KEY=your_claude_api_key_here"
```

## 🧪 **Step 3: Test Deployment**

### **Get Service URL:**
```bash
# Get the service URL
gcloud run services describe seranking-seo-api-enhanced \
  --region us-central1 \
  --project titanium-gadget-451710-i7 \
  --format="value(status.url)"
```

### **Test Health Endpoint:**
```bash
# Test health endpoint
curl https://seranking-seo-api-enhanced-XXXXX.us-central1.run.app/health
```

### **Test SEO Opportunities:**
```bash
# Test SEO opportunities endpoint
curl -X POST https://seranking-seo-api-enhanced-XXXXX.us-central1.run.app/api/seo-opportunities \
  -H "Content-Type: application/json" \
  -d '{"domain": "seranking.com", "market": "us"}'
```

### **Test Enhanced Report:**
```bash
# Test enhanced report endpoint
curl -X POST https://seranking-seo-api-enhanced-XXXXX.us-central1.run.app/api/enhanced-report \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "seranking.com",
    "market": "us",
    "keywords": ["seo tools", "keyword research"],
    "competitors": ["ahrefs.com", "semrush.com"]
  }'
```

## 📊 **Step 4: Update n8n Workflow**

### **Update HTTP Request Node:**
```json
{
  "method": "POST",
  "url": "https://seranking-seo-api-enhanced-XXXXX.us-central1.run.app/api/enhanced-report",
  "body": {
    "domain": "{{ $json.domain || 'seranking.com' }}",
    "market": "{{ $json.market || 'us' }}",
    "keywords": "{{ $json.keywords || ['seo tools', 'keyword research'] }}",
    "competitors": "{{ $json.competitors || ['ahrefs.com', 'semrush.com'] }}"
  }
}
```

## 🔐 **Step 5: Security Best Practices**

### **Environment Variables:**
- ✅ **Never commit API keys** to GitHub
- ✅ **Use Google Cloud Secret Manager** for production
- ✅ **Set environment variables** in Cloud Run
- ✅ **Use .gitignore** to exclude sensitive files

### **API Security:**
- ✅ **Rate limiting** implemented
- ✅ **Input validation** for all endpoints
- ✅ **Error handling** for all operations
- ✅ **Timeout protection** (900 seconds)

## 📈 **Step 6: Monitoring & Logs**

### **View Logs:**
```bash
# View service logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=seranking-seo-api-enhanced" \
  --project titanium-gadget-451710-i7 \
  --limit 50
```

### **Monitor Performance:**
```bash
# Check service status
gcloud run services describe seranking-seo-api-enhanced \
  --region us-central1 \
  --project titanium-gadget-451710-i7
```

## 🎯 **Step 7: Production Checklist**

### **✅ Pre-Deployment:**
- [ ] All code pushed to GitHub
- [ ] Environment variables set
- [ ] API keys configured
- [ ] Dockerfile updated
- [ ] Tests passing locally

### **✅ Post-Deployment:**
- [ ] Health endpoint responding
- [ ] SEO opportunities endpoint working
- [ ] Enhanced report endpoint working
- [ ] n8n workflow updated
- [ ] Slack notifications working

## 🚀 **Deployment Commands Summary:**

```bash
# 1. Set project
gcloud config set project titanium-gadget-451710-i7

# 2. Deploy API
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
  --project titanium-gadget-451710-i7

# 3. Set environment variables
gcloud run services update seranking-seo-api-enhanced \
  --region us-central1 \
  --project titanium-gadget-451710-i7 \
  --set-env-vars="SERANKING_API_KEY=b931695c-9e38-cde4-4d4b-49eeb217118f,ANTHROPIC_API_KEY=your_claude_api_key_here"

# 4. Get service URL
gcloud run services describe seranking-seo-api-enhanced \
  --region us-central1 \
  --project titanium-gadget-451710-i7 \
  --format="value(status.url)"
```

## 🎉 **Success!**

Your enhanced SEO Intelligence API will be deployed at:
`https://seranking-seo-api-enhanced-XXXXX.us-central1.run.app`

**Features Available:**
- ✅ SEO Opportunity Analysis
- ✅ Enhanced AI Insights
- ✅ Competitive Gap Analysis
- ✅ Low-Hanging Fruit Detection
- ✅ Comprehensive Reporting
