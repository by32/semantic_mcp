#!/usr/bin/env python3
"""Test the standalone MCP server"""

import subprocess
import json

def test_standalone_mcp():
    print("🧪 Testing Standalone MCP Server for LangFlow Desktop")
    print("=" * 55)
    
    process = subprocess.Popen(
        ['python3', '/Users/byoungs/Documents/gitlab/semantic_mcp/standalone_mcp_server.py'],
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
        
        # Test 4: Call tool
        query_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "query_semantic_layer",
                "arguments": {
                    "description": "Show me the top 5 most populous cities"
                }
            },
            "id": 3
        }
        
        print("4️⃣  Testing query tool...")
        process.stdin.write(json.dumps(query_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline().strip()
        print(f"   ✅ Response: {response[:80]}...")
        
        query_data = json.loads(response)
        if "result" in query_data:
            content = query_data["result"]["content"][0]["text"]
            data = json.loads(content)
            if "result" in data and "data" in data["result"]:
                cities = data["result"]["data"]
                print(f"   ✅ Got {len(cities)} cities:")
                for city in cities[:3]:  # Show first 3
                    print(f"      - {city['cities.city_name']}: {city['cities.total_population']}")
        
        print("\n🎉 Standalone MCP server is working!")
        print("\nFor LangFlow Desktop, try this command instead:")
        print(f"/usr/bin/python3 {'/Users/byoungs/Documents/gitlab/semantic_mcp/standalone_mcp_server.py'}")
        
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
    test_standalone_mcp()