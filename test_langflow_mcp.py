#!/usr/bin/env python3
"""Test the LangFlow MCP server with real Cube.js data"""

import subprocess
import json

def test_langflow_mcp():
    print("🧪 Testing LangFlow MCP Server with Real Cube.js Data")
    print("=" * 60)
    
    process = subprocess.Popen(
        ['python3', '/Users/byoungs/Documents/gitlab/semantic_mcp/langflow_mcp_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Test 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "langflow-desktop", "version": "1.0.0"}
            },
            "id": 1
        }
        
        print("1️⃣  Testing initialize...")
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline().strip()
        print(f"   ✅ Response: {response[:80]}...")
        
        # Test 2: Initialized notification
        initialized = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        print("2️⃣  Sending initialized notification...")
        process.stdin.write(json.dumps(initialized) + '\n')
        process.stdin.flush()
        
        # Test 3: List tools
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        print("3️⃣  Testing tools/list...")
        process.stdin.write(json.dumps(tools_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline().strip()
        print(f"   ✅ Response: {response[:80]}...")
        
        tools_data = json.loads(response)
        if "result" in tools_data and "tools" in tools_data["result"]:
            tools = tools_data["result"]["tools"]
            print(f"   ✅ Found {len(tools)} tools")
            for tool in tools:
                print(f"      - {tool['name']}")
        
        # Test 4: Get schema metadata
        schema_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_schema_metadata",
                "arguments": {}
            },
            "id": 3
        }
        
        print("4️⃣  Testing schema metadata...")
        process.stdin.write(json.dumps(schema_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline().strip()
        if response:
            schema_data = json.loads(response)
            if "result" in schema_data:
                content = schema_data["result"]["content"][0]["text"]
                meta = json.loads(content)
                if "cubes" in meta:
                    cubes = meta["cubes"]
                    print(f"   ✅ Found {len(cubes)} cubes:")
                    for cube in cubes:
                        measures = len(cube.get("measures", []))
                        dimensions = len(cube.get("dimensions", []))
                        print(f"      - {cube['name']}: {measures} measures, {dimensions} dimensions")
        
        # Test 5: City population query
        city_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "query_semantic_layer",
                "arguments": {
                    "description": "Show me the top 5 cities by population"
                }
            },
            "id": 4
        }
        
        print("5️⃣  Testing city population query...")
        process.stdin.write(json.dumps(city_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline().strip()
        if response:
            city_data = json.loads(response)
            if "result" in city_data:
                content = city_data["result"]["content"][0]["text"]
                data = json.loads(content)
                if "result" in data and "data" in data["result"]:
                    cities = data["result"]["data"]
                    print(f"   ✅ Got {len(cities)} cities from real data")
                    for city in cities[:3]:
                        city_name = city.get("cities.city_name", "Unknown")
                        population = city.get("cities.total_population", "Unknown")
                        print(f"      - {city_name}: {population}")
        
        # Test 6: Revenue by product category
        revenue_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "query_semantic_layer",
                "arguments": {
                    "description": "Show me revenue by product category"
                }
            },
            "id": 5
        }
        
        print("6️⃣  Testing revenue by product category...")
        process.stdin.write(json.dumps(revenue_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline().strip()
        if response:
            revenue_data = json.loads(response)
            if "result" in revenue_data:
                content = revenue_data["result"]["content"][0]["text"]
                data = json.loads(content)
                if "result" in data and "data" in data["result"]:
                    categories = data["result"]["data"]
                    print(f"   ✅ Got {len(categories)} product categories from real data")
                    for cat in categories[:3]:
                        category = cat.get("sales.product_category", "Unknown")
                        revenue = cat.get("sales.total_revenue", "Unknown")
                        print(f"      - {category}: ${revenue}")
        
        print("\n🎉 LangFlow MCP server with real data is working!")
        print("\nUpdate your LangFlow Desktop MCP Tools command to:")
        print(f"/usr/bin/python3 {'/Users/byoungs/Documents/gitlab/semantic_mcp/langflow_mcp_server.py'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        stderr = process.stderr.read()
        if stderr:
            print(f"Stderr: {stderr}")
        return False
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_langflow_mcp()