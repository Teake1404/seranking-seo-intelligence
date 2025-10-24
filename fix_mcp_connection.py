#!/usr/bin/env python3
"""
Fix MCP connection by using direct SEranking API calls
This will make your current API work with real data
"""
import requests
import json
import os

def get_seranking_data_direct(keywords, domain, api_key):
    """Get data directly from SEranking API"""
    try:
        # SEranking API endpoint
        url = "https://api4.seranking.com/v1/keywords/rankings"
        
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        
        # Get rankings for domain
        params = {
            "domain": domain,
            "keywords": keywords
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"SEranking API error: {response.status_code}")
            return {}
            
    except Exception as e:
        print(f"Error getting SEranking data: {e}")
        return {}

def test_seranking_connection():
    """Test SEranking API connection"""
    api_key = "b931695c-9e38-cde4-4d4b-49eeb217118f"
    
    print("🔍 Testing SEranking API connection...")
    
    # Test with a simple request
    test_data = get_seranking_data_direct(
        keywords=["seo tools"],
        domain="seranking.com", 
        api_key=api_key
    )
    
    if test_data:
        print("✅ SEranking API connection successful!")
        print(f"Data received: {json.dumps(test_data, indent=2)[:200]}...")
        return True
    else:
        print("❌ SEranking API connection failed")
        return False

if __name__ == "__main__":
    test_seranking_connection()
