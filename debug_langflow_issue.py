#!/usr/bin/env python3
"""Debug what's causing the LangFlow 400 error"""

import json
import urllib.request
import urllib.parse

# Test problematic queries that might cause 400 errors
problematic_queries = [
    {},  # Empty query
    {"measures": []},  # Empty measures
    {"dimensions": []},  # Empty dimensions
    {"measures": [], "dimensions": []},  # Both empty
    {"filters": []},  # Only filters
    {"invalid_field": "test"},  # Invalid field
]

def test_cube_query(query):
    """Test a query directly against Cube.js"""
    url = "http://localhost:4000/cubejs-api/v1/load"
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"query": query}).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            return f"✅ Success: {len(result.get('data', []))} rows"
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else "No details"
        return f"❌ HTTP Error {e.code}: {error_body[:200]}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

print("🔍 Testing problematic queries against Cube.js")
print("=" * 50)

for i, query in enumerate(problematic_queries, 1):
    print(f"{i}. Query: {query}")
    result = test_cube_query(query)
    print(f"   Result: {result}")
    print()

# Test some queries that should work
print("✅ Testing valid queries:")
valid_queries = [
    {"measures": ["cities.count"]},
    {"measures": ["sales.total_revenue"], "dimensions": ["sales.product_category"]},
    {"dimensions": ["cities.city_name"], "limit": 5},
]

for i, query in enumerate(valid_queries, 1):
    print(f"{i}. Query: {query}")
    result = test_cube_query(query)
    print(f"   Result: {result}")
    print()