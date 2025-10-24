#!/usr/bin/env python3
"""
SEO Opportunity Analysis using SEranking MCP
Identifies low-hanging fruit opportunities and competitive gaps
"""
import subprocess
import json
import time
from typing import Dict, List, Any

class SEOOpportunityAnalyzer:
    """Analyze SEO opportunities using SEranking MCP"""
    
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.domain = "seranking.com"
        self.market = "us"
        
    def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call SEranking MCP tool"""
        mcp_request = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            process = subprocess.Popen(
                ["docker", "run", "-i", "--rm", "-e", f"SERANKING_API_TOKEN={self.api_token}", "se-ranking/seo-data-api-mcp-server"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=json.dumps(mcp_request) + "\n", timeout=120)
            
            if process.returncode != 0:
                return {"error": f"Process failed: {stderr}"}
            
            response = json.loads(stdout.strip())
            return response
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_domain_performance(self) -> Dict[str, Any]:
        """Step 1: Analyze domain's keyword performance"""
        print("🔍 Step 1: Analyzing domain performance...")
        
        results = {
            "lost_keywords": [],
            "declining_keywords": [],
            "domain_overview": {}
        }
        
        # Get lost keywords
        print("   📉 Finding lost keywords...")
        lost_response = self.call_mcp_tool("domainKeywords", {
            "source": self.market,
            "domain": self.domain,
            "pos_change": "lost",
            "limit": 50
        })
        
        if "result" in lost_response and "content" in lost_response["result"]:
            try:
                lost_data = json.loads(lost_response["result"]["content"][0]["text"])
                results["lost_keywords"] = lost_data[:20]  # Top 20 lost keywords
                print(f"   ✅ Found {len(lost_data)} lost keywords")
            except:
                print("   ❌ Failed to parse lost keywords")
        
        # Get declining keywords
        print("   📉 Finding declining keywords...")
        declining_response = self.call_mcp_tool("domainKeywords", {
            "source": self.market,
            "domain": self.domain,
            "pos_change": "down",
            "limit": 50
        })
        
        if "result" in declining_response and "content" in declining_response["result"]:
            try:
                declining_data = json.loads(declining_response["result"]["content"][0]["text"])
                results["declining_keywords"] = declining_data[:20]  # Top 20 declining
                print(f"   ✅ Found {len(declining_data)} declining keywords")
            except:
                print("   ❌ Failed to parse declining keywords")
        
        return results
    
    def competitive_analysis(self) -> Dict[str, Any]:
        """Step 2: Conduct competitive analysis"""
        print("\n🏆 Step 2: Competitive analysis...")
        
        results = {
            "top_competitors": [],
            "competitor_keywords": []
        }
        
        # Get competitors
        print("   🔍 Finding competitors...")
        competitors_response = self.call_mcp_tool("domainCompetitors", {
            "source": self.market,
            "domain": self.domain,
            "stats": 1
        })
        
        if "result" in competitors_response and "content" in competitors_response["result"]:
            try:
                competitors_data = json.loads(competitors_response["result"]["content"][0]["text"])
                # Sort by common_keywords DESC and get top 2
                sorted_competitors = sorted(competitors_data, key=lambda x: x.get("common_keywords", 0), reverse=True)
                results["top_competitors"] = sorted_competitors[:2]
                print(f"   ✅ Found {len(sorted_competitors)} competitors")
                for i, comp in enumerate(results["top_competitors"], 1):
                    print(f"     {i}. {comp.get('domain', 'Unknown')} - {comp.get('common_keywords', 0)} common keywords")
            except:
                print("   ❌ Failed to parse competitors")
        
        # Get competitor keywords we don't rank for
        if results["top_competitors"]:
            print("   🔍 Finding competitor keywords we don't rank for...")
            for competitor in results["top_competitors"]:
                comp_domain = competitor.get("domain")
                if comp_domain:
                    print(f"   📊 Analyzing {comp_domain}...")
                    comparison_response = self.call_mcp_tool("domainKeywordsComparison", {
                        "source": self.market,
                        "domain": comp_domain,
                        "compare": self.domain,
                        "diff": 1,  # Keywords they have, we don't
                        "order_field": "volume",
                        "order_type": "desc",
                        "limit": 30
                    })
                    
                    if "result" in comparison_response and "content" in comparison_response["result"]:
                        try:
                            comp_keywords = json.loads(comparison_response["result"]["content"][0]["text"])
                            results["competitor_keywords"].extend(comp_keywords[:15])  # Top 15 per competitor
                            print(f"     ✅ Found {len(comp_keywords)} keywords we don't rank for")
                        except:
                            print(f"     ❌ Failed to parse keywords for {comp_domain}")
        
        return results
    
    def find_keyword_opportunities(self, competitor_keywords: List[Dict]) -> Dict[str, Any]:
        """Step 3: Find new keyword opportunities"""
        print("\n💡 Step 3: Finding keyword opportunities...")
        
        results = {
            "related_keywords": [],
            "similar_keywords": []
        }
        
        # Take top 10 competitor keywords
        top_keywords = competitor_keywords[:10]
        print(f"   🔍 Analyzing {len(top_keywords)} competitor keywords...")
        
        for i, keyword_data in enumerate(top_keywords, 1):
            keyword = keyword_data.get("keyword", "")
            if not keyword:
                continue
                
            print(f"   📊 {i}/10: Analyzing '{keyword}'...")
            
            # Get related keywords
            related_response = self.call_mcp_tool("keywordsRelated", {
                "source": self.market,
                "keyword": keyword,
                "limit": 5,
                "sort": "volume",
                "sort_order": "desc"
            })
            
            if "result" in related_response and "content" in related_response["result"]:
                try:
                    related_data = json.loads(related_response["result"]["content"][0]["text"])
                    for rel_kw in related_data[:5]:
                        rel_kw["source_keyword"] = keyword
                        results["related_keywords"].append(rel_kw)
                except:
                    pass
            
            # Get similar keywords
            similar_response = self.call_mcp_tool("keywordsSimilar", {
                "source": self.market,
                "keyword": keyword,
                "limit": 5,
                "sort": "volume",
                "sort_order": "desc"
            })
            
            if "result" in similar_response and "content" in similar_response["result"]:
                try:
                    similar_data = json.loads(similar_response["result"]["content"][0]["text"])
                    for sim_kw in similar_data[:5]:
                        sim_kw["source_keyword"] = keyword
                        results["similar_keywords"].append(sim_kw)
                except:
                    pass
        
        return results
    
    def synthesize_report(self, performance_data: Dict, competitive_data: Dict, opportunities_data: Dict) -> str:
        """Step 4: Create final report"""
        print("\n📊 Step 4: Creating final report...")
        
        report = f"""
# 🚀 SEO Opportunity Analysis Report
## Domain: {self.domain} | Market: {self.market.upper()}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

---

## 📉 Domain Performance Issues

### Lost Keywords ({len(performance_data.get('lost_keywords', []))} found)
"""
        
        # Add lost keywords
        for i, kw in enumerate(performance_data.get('lost_keywords', [])[:10], 1):
            report += f"{i}. **{kw.get('keyword', 'Unknown')}** - Volume: {kw.get('volume', 0):,} | CPC: ${kw.get('cpc', 0):.2f}\n"
        
        report += f"\n### Declining Keywords ({len(performance_data.get('declining_keywords', []))} found)\n"
        
        # Add declining keywords
        for i, kw in enumerate(performance_data.get('declining_keywords', [])[:10], 1):
            report += f"{i}. **{kw.get('keyword', 'Unknown')}** - Position: {kw.get('position', 'N/A')} | Volume: {kw.get('volume', 0):,}\n"
        
        report += f"\n---\n\n## 🏆 Competitive Analysis\n\n### Top Competitors\n"
        
        # Add competitors
        for i, comp in enumerate(competitive_data.get('top_competitors', []), 1):
            report += f"{i}. **{comp.get('domain', 'Unknown')}** - {comp.get('common_keywords', 0)} common keywords\n"
        
        report += f"\n### Competitor Keywords We Don't Rank For ({len(competitive_data.get('competitor_keywords', []))} found)\n"
        
        # Add competitor keywords
        for i, kw in enumerate(competitive_data.get('competitor_keywords', [])[:15], 1):
            report += f"{i}. **{kw.get('keyword', 'Unknown')}** - Volume: {kw.get('volume', 0):,} | CPC: ${kw.get('cpc', 0):.2f}\n"
        
        report += f"\n---\n\n## 💡 New Keyword Opportunities\n\n### Related Keywords ({len(opportunities_data.get('related_keywords', []))} found)\n"
        
        # Add related keywords
        for i, kw in enumerate(opportunities_data.get('related_keywords', [])[:15], 1):
            report += f"{i}. **{kw.get('keyword', 'Unknown')}** - Volume: {kw.get('volume', 0):,} | CPC: ${kw.get('cpc', 0):.2f} | Difficulty: {kw.get('difficulty', 'N/A')}\n"
        
        report += f"\n### Similar Keywords ({len(opportunities_data.get('similar_keywords', []))} found)\n"
        
        # Add similar keywords
        for i, kw in enumerate(opportunities_data.get('similar_keywords', [])[:15], 1):
            report += f"{i}. **{kw.get('keyword', 'Unknown')}** - Volume: {kw.get('volume', 0):,} | CPC: ${kw.get('cpc', 0):.2f} | Difficulty: {kw.get('difficulty', 'N/A')}\n"
        
        # Low-hanging fruit analysis
        report += f"\n---\n\n## 🎯 Low-Hanging Fruit Opportunities\n\n"
        
        # Analyze opportunities for low-hanging fruit
        all_opportunities = opportunities_data.get('related_keywords', []) + opportunities_data.get('similar_keywords', [])
        
        # Filter for low difficulty, high volume
        low_hanging = [
            kw for kw in all_opportunities 
            if kw.get('difficulty', 100) < 30 and kw.get('volume', 0) > 1000
        ]
        
        # Sort by volume
        low_hanging.sort(key=lambda x: x.get('volume', 0), reverse=True)
        
        report += f"### Top Low-Hanging Fruit ({len(low_hanging)} opportunities)\n"
        report += "*Keywords with difficulty < 30 and volume > 1,000*\n\n"
        
        for i, kw in enumerate(low_hanging[:10], 1):
            report += f"{i}. **{kw.get('keyword', 'Unknown')}**\n"
            report += f"   - Volume: {kw.get('volume', 0):,}/month\n"
            report += f"   - CPC: ${kw.get('cpc', 0):.2f}\n"
            report += f"   - Difficulty: {kw.get('difficulty', 'N/A')}\n"
            report += f"   - Source: {kw.get('source_keyword', 'Unknown')}\n\n"
        
        report += f"\n---\n\n## 📈 Recommendations\n\n"
        report += f"1. **Immediate Action**: Focus on the {len(low_hanging)} low-hanging fruit opportunities\n"
        report += f"2. **Content Strategy**: Create content targeting high-volume, low-difficulty keywords\n"
        report += f"3. **Competitive Monitoring**: Track the top {len(competitive_data.get('top_competitors', []))} competitors regularly\n"
        report += f"4. **Recovery Plan**: Address the {len(performance_data.get('lost_keywords', []))} lost keywords\n"
        
        return report
    
    def run_full_analysis(self) -> str:
        """Run complete SEO opportunity analysis"""
        print("🚀 Starting SEO Opportunity Analysis...")
        print(f"Domain: {self.domain} | Market: {self.market}")
        print("=" * 60)
        
        # Step 1: Domain performance
        performance_data = self.analyze_domain_performance()
        
        # Step 2: Competitive analysis
        competitive_data = self.competitive_analysis()
        
        # Step 3: Keyword opportunities
        opportunities_data = self.find_keyword_opportunities(competitive_data.get('competitor_keywords', []))
        
        # Step 4: Generate report
        report = self.synthesize_report(performance_data, competitive_data, opportunities_data)
        
        print("\n✅ Analysis complete!")
        return report

def main():
    """Run the SEO opportunity analysis"""
    api_token = "b931695c-9e38-cde4-4d4b-49eeb217118f"
    
    analyzer = SEOOpportunityAnalyzer(api_token)
    report = analyzer.run_full_analysis()
    
    # Save report
    with open("seo_opportunity_report.md", "w") as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: seo_opportunity_report.md")
    print("\n" + "="*60)
    print(report)

if __name__ == "__main__":
    main()

