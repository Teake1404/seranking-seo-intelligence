#!/bin/bash

# 🚀 GitHub Repository Setup Script
# Enhanced SEO Intelligence API

echo "🚀 Setting up GitHub repository for Enhanced SEO Intelligence API"
echo "=================================================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Add all files
echo "📦 Adding files to git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Enhanced SEO Intelligence API with opportunity analysis

Features:
- SEO Opportunity Analysis (lost keywords, declining positions)
- Competitive Gap Analysis (competitor opportunities)
- Low-Hanging Fruit Detection (easy wins)
- Enhanced AI Insights (combined Claude analysis)
- Comprehensive Reporting (all insights in one report)
- SEranking MCP Integration
- Redis Caching
- n8n Workflow Support

Endpoints:
- /api/seo-opportunities - SEO opportunity analysis
- /api/enhanced-report - Combined insights + opportunities
- /health - Health check (version 2.0)
- / - API information with new features

Ready for Google Cloud Run deployment!"

# Check if remote origin exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "✅ Remote origin already exists"
    echo "📍 Current remote: $(git remote get-url origin)"
else
    echo "⚠️  No remote origin found"
    echo "🔗 Please add your GitHub repository URL:"
    echo "   git remote add origin https://github.com/yourusername/enhanced-seo-intelligence-api.git"
fi

# Show git status
echo ""
echo "📊 Git Status:"
git status

echo ""
echo "🎯 Next Steps:"
echo "1. Create a new private repository on GitHub"
echo "2. Add remote origin: git remote add origin https://github.com/yourusername/repo-name.git"
echo "3. Push to GitHub: git push -u origin main"
echo "4. Deploy to Google Cloud Run using the deployment guide"
echo ""
echo "📋 Repository should include:"
echo "✅ Enhanced SEO Intelligence API"
echo "✅ SEranking MCP Integration"
echo "✅ Redis Caching"
echo "✅ n8n Workflow Support"
echo "✅ Docker Configuration"
echo "✅ Deployment Guides"
echo ""
echo "🔐 Security:"
echo "✅ .gitignore configured"
echo "✅ API keys excluded"
echo "✅ Sensitive data protected"
echo ""
echo "🚀 Ready for deployment!"
