#!/usr/bin/env python3
"""Test the AWS MCP Bridge"""

import subprocess
import json
import sys
import os

def test_aws_bridge():
    """Test the AWS MCP Bridge functionality"""
    
    print("🧪 Testing AWS MCP Bridge")
    print("=" * 30)
    
    # Check if bridge is configured
    bridge_script = "aws-mcp-bridge-configured.py"
    
    if not os.path.exists(bridge_script):
        print("❌ Bridge not configured. Please run ./setup-aws-bridge.sh first")
        return False
    
    # Start the bridge
    process = subprocess.Popen(
        ['python3', bridge_script],
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
                "clientInfo": {"name": "aws-bridge-test", "version": "1.0.0"}
            },
            "id": 1
        }
        
        print("1. Testing initialize...")
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline().strip()
        if response:
            data = json.loads(response)
            if "result" in data:
                print("   ✅ Initialize successful")
                server_name = data["result"]["serverInfo"]["name"]
                print(f"   📡 Connected to: {server_name}")
            else:
                print(f"   ❌ Initialize failed: {data.get('error', {}).get('message', 'Unknown error')}")
                return False
        else:
            print("   ❌ No response received")
            return False
        
        # Test 2: List tools
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        print("2. Testing tools/list...")
        process.stdin.write(json.dumps(tools_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline().strip()
        if response:
            data = json.loads(response)
            if "result" in data and "tools" in data["result"]:
                tools = data["result"]["tools"]
                print(f"   ✅ Found {len(tools)} tools")
                for tool in tools:
                    print(f"      - {tool['name']}")
            else:
                print(f"   ❌ Tools list failed: {data.get('error', {}).get('message', 'Unknown error')}")
                return False
        else:
            print("   ❌ No response received")
            return False
        
        # Test 3: Query semantic layer
        query_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "query_semantic_layer",
                "arguments": {
                    "description": "Show me revenue by product category"
                }
            },
            "id": 3
        }
        
        print("3. Testing query_semantic_layer...")
        process.stdin.write(json.dumps(query_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline().strip()
        if response:
            data = json.loads(response)
            if "result" in data:
                print("   ✅ Query successful")
                content = data["result"]["content"][0]["text"]
                try:
                    parsed = json.loads(content)
                    if "result" in parsed:
                        result_data = parsed["result"]
                        if "data" in result_data:
                            rows = result_data["data"]
                            print(f"   📊 Got {len(rows)} rows of data")
                            for row in rows[:3]:  # Show first 3 rows
                                print(f"      - {row}")
                        else:
                            print(f"   📊 Query result: {result_data}")
                    else:
                        print(f"   📊 Response: {content[:100]}...")
                except:
                    print(f"   📊 Raw response: {content[:100]}...")
            else:
                print(f"   ❌ Query failed: {data.get('error', {}).get('message', 'Unknown error')}")
                return False
        else:
            print("   ❌ No response received")
            return False
        
        print("\n🎉 AWS Bridge test successful!")
        print("✅ Ready for LangFlow integration")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        process.terminate()
        process.wait()
        
        # Check stderr for any debug output
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"\nDebug output:\n{stderr_output}")

if __name__ == "__main__":
    success = test_aws_bridge()
    sys.exit(0 if success else 1)