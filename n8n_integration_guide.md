# n8n Integration Guide for SEO Insights MCP

## 🚀 Quick Setup

### 1. Install the MCP Server

```bash
# Clone the repository
git clone https://github.com/yourusername/seo-insights-mcp.git
cd seo-insights-mcp

# Install dependencies
pip install -r requirements_mcp.txt
```

### 2. Configure MCP Client

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "seo-insights": {
      "command": "python",
      "args": ["/path/to/seo-insights-mcp/seo_insights_mcp.py"],
      "env": {
        "PYTHONPATH": "/path/to/seo-insights-mcp"
      }
    }
  }
}
```

### 3. n8n Workflow Integration

#### Basic Workflow Structure:
```
SEranking MCP → SEO Insights MCP → Claude AI → Output
```

#### Detailed n8n Nodes:

1. **SEranking MCP Node**
   - Get keyword rankings
   - Get competitor data
   - Get backlink data

2. **SEO Insights MCP Node**
   - Tool: `analyze_seo_insights`
   - Input: Rankings, competitors, backlinks data
   - Output: Comprehensive analysis

3. **Claude AI Node**
   - Process SEO insights
   - Generate natural language recommendations
   - Create actionable reports

4. **Output Node**
   - Format final report
   - Send notifications
   - Store results

## 🔧 Configuration Examples

### SEO Insights MCP Node Configuration

```json
{
  "tool": "analyze_seo_insights",
  "parameters": {
    "rankings_data": "{{ $json.rankings }}",
    "competitors_data": "{{ $json.competitors }}",
    "backlinks_data": "{{ $json.backlinks }}",
    "domain": "{{ $json.domain }}",
    "market": "{{ $json.market }}"
  }
}
```

### Claude AI Prompt Template

```
You are an SEO expert analyzing the following data:

SEO Analysis Results:
{{ $json.analysis }}

Key Metrics:
- Visibility Score: {{ $json.analysis.visibility.score }}%
- Page 1 Keywords: {{ $json.analysis.visibility.page_1_keywords }}
- Opportunities Found: {{ $json.analysis.opportunities.length }}
- Anomalies Detected: {{ $json.analysis.anomalies.length }}

Please provide:
1. Executive summary of SEO performance
2. Top 3 actionable recommendations
3. Priority areas for improvement
4. Competitive insights and opportunities
```

## 📊 Expected Output Format

### SEO Insights MCP Output:
```json
{
  "domain": "example.com",
  "market": "uk",
  "timestamp": "2024-01-01T00:00:00Z",
  "analysis": {
    "visibility": {
      "score": 75.5,
      "total_keywords": 50,
      "page_1_keywords": 12,
      "page_1_percentage": 24.0
    },
    "anomalies": [
      {
        "keyword": "example keyword",
        "current_position": 15,
        "expected_position": 8,
        "severity": "high",
        "change_type": "decline"
      }
    ],
    "opportunities": [
      {
        "keyword": "high volume keyword",
        "current_position": 25,
        "search_volume": 10000,
        "opportunity_score": 0.85,
        "priority": "high"
      }
    ],
    "competitive": {
      "top_competitors": [...],
      "market_leader": {...},
      "competitive_gaps": [...]
    }
  },
  "summary": {
    "overview": {...},
    "key_insights": [...],
    "recommendations": [...]
  }
}
```

## 🎯 Advanced Use Cases

### 1. Automated SEO Monitoring
- Daily anomaly detection
- Weekly opportunity analysis
- Monthly competitive reports

### 2. Content Strategy Optimization
- Identify high-opportunity keywords
- Analyze competitor content gaps
- Prioritize content creation

### 3. Technical SEO Analysis
- Monitor ranking stability
- Detect algorithm impacts
- Track visibility trends

## 🔍 Troubleshooting

### Common Issues:

1. **MCP Server Not Found**
   - Check Python path in configuration
   - Verify dependencies are installed
   - Test server manually: `python seo_insights_mcp.py`

2. **Data Parsing Errors**
   - Ensure input data format matches expected schema
   - Check for required fields (keyword, position, volume)
   - Validate JSON structure

3. **Performance Issues**
   - Limit data size for large datasets
   - Use pagination for extensive keyword lists
   - Monitor memory usage

### Debug Mode:
```bash
# Run with debug logging
PYTHONPATH=. python seo_insights_mcp.py --debug
```

## 📈 Performance Optimization

### Recommended Settings:
- **Max keywords per analysis**: 1000
- **Historical data points**: 30 days
- **Competitor limit**: 50
- **Analysis frequency**: Daily

### Memory Usage:
- **Base memory**: ~50MB
- **Per 1000 keywords**: +10MB
- **Historical data**: +5MB per month

## 🔐 Security Considerations

- Keep API keys secure
- Use environment variables for configuration
- Implement rate limiting for production use
- Monitor for unusual data patterns

## 📞 Support

For issues and questions:
- GitHub Issues: [Repository Issues](https://github.com/yourusername/seo-insights-mcp/issues)
- Documentation: [README_MCP.md](README_MCP.md)
- Examples: [test_mcp_server.py](test_mcp_server.py)
