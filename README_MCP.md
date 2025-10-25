# SEO Insights MCP Server

Advanced SEO analysis MCP server providing comprehensive insights including anomaly detection, opportunity analysis, competitive intelligence, and visibility scoring.

## Features

### 🔍 **Anomaly Detection**
- Statistical analysis of ranking changes using Z-scores
- Identifies significant ranking drops or improvements
- Severity classification (high/medium/low)
- Change type detection (improvement/decline)

### 🎯 **Opportunity Analysis**
- Advanced scoring algorithm for SEO opportunities
- Traffic potential estimation
- Priority classification (high/medium/low)
- Keyword difficulty and volume analysis

### 🏆 **Competitive Analysis**
- Top competitor identification
- Common keyword analysis
- Competitive gap identification
- Market leader analysis

### 📊 **Visibility Scoring**
- Comprehensive visibility metrics
- Position-based scoring system
- Page 1 keyword tracking
- Performance breakdown by position ranges

## Installation

1. Install dependencies:
```bash
pip install -r requirements_mcp.txt
```

2. Configure MCP server in your MCP client configuration:
```json
{
  "mcpServers": {
    "seo-insights": {
      "command": "python",
      "args": ["seo_insights_mcp.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

## Usage

### Available Tools

1. **analyze_seo_insights** - Comprehensive SEO analysis
2. **detect_anomalies** - Statistical anomaly detection
3. **analyze_opportunities** - SEO opportunity identification
4. **competitive_analysis** - Competitive landscape analysis
5. **visibility_analysis** - Visibility metrics calculation

### Example Usage

```python
# Comprehensive analysis
result = await mcp_client.call_tool("analyze_seo_insights", {
    "rankings_data": [
        {
            "keyword": "personalised gifts",
            "position": 15,
            "volume": 12000,
            "cpc": 0.85,
            "difficulty": 65,
            "traffic": 1200,
            "prev_pos": 18
        }
    ],
    "competitors_data": [
        {
            "domain": "amazon.co.uk",
            "common_keywords": 117838
        }
    ],
    "domain": "bagsoflove.co.uk",
    "market": "uk"
})
```

## Output Format

The MCP server returns structured JSON data including:

- **Visibility Analysis**: Scores, metrics, and breakdowns
- **Anomaly Detection**: Statistical analysis of ranking changes
- **Opportunity Analysis**: Prioritized SEO opportunities
- **Competitive Analysis**: Market landscape and gaps
- **Summary Report**: Key insights and recommendations

## Advanced Features

### Statistical Analysis
- Z-score based anomaly detection
- Confidence intervals for ranking predictions
- Trend analysis capabilities

### Machine Learning Ready
- Extensible scoring algorithms
- Configurable thresholds
- Historical data integration

### Performance Optimized
- Efficient data processing
- Minimal memory footprint
- Fast response times

## Integration with n8n

This MCP server is designed to work seamlessly with n8n workflows:

1. **Data Input**: Accepts data from SEranking MCP and other sources
2. **Processing**: Performs advanced SEO analysis
3. **Output**: Structured data ready for Claude AI interpretation
4. **Reporting**: Generates comprehensive insights and recommendations

## Configuration

### Thresholds
- `anomaly_threshold`: Z-score threshold for anomaly detection (default: 2.0)
- `opportunity_threshold`: Minimum opportunity score (default: 0.7)

### Scoring Weights
- Position factor: 40%
- Volume factor: 30%
- Difficulty factor: 20%
- CPC factor: 10%

## License

MIT License - See LICENSE file for details.
