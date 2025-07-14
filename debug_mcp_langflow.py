#!/usr/bin/env python3
"""Debug MCP connection issues with LangFlow"""

import subprocess
import json
import time

def test_mcp_with_proper_sequence():
    """Test the exact sequence LangFlow would use"""
    
    print("Testing MCP server with LangFlow-style connection...")
    
    # Start the MCP server
    process = subprocess.Popen(
        ['/Users/byoungs/Documents/gitlab/semantic_mcp/scripts/langflow-mcp-wrapper.sh'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0  # Unbuffered
    )
    
    try:
        # Step 1: Initialize (exactly as LangFlow would)
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "langflow",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        print("1. Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        # Read initialize response
        init_response = process.stdout.readline().strip()
        print(f"   Response: {init_response}")
        
        if not init_response:
            stderr_output = process.stderr.read()
            print(f"   Stderr: {stderr_output}")
            return
        
        # Step 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        print("2. Sending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification) + '\n')
        process.stdin.flush()
        
        # Give server time to process
        time.sleep(0.1)
        
        # Step 3: List tools
        tools_request = {
            "jsonrpc": "2.0", 
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        print("3. Requesting tools list...")
        process.stdin.write(json.dumps(tools_request) + '\n')
        process.stdin.flush()
        
        # Read tools response
        tools_response = process.stdout.readline().strip()
        print(f"   Response: {tools_response}")
        
        # Parse and display tools
        if tools_response:
            try:
                tools_data = json.loads(tools_response)
                if "result" in tools_data and "tools" in tools_data["result"]:
                    tools = tools_data["result"]["tools"]
                    print(f"\n✅ SUCCESS: Found {len(tools)} tools:")
                    for tool in tools:
                        print(f"   - {tool['name']}: {tool.get('description', 'No description')}")
                elif "error" in tools_data:
                    print(f"\n❌ ERROR: {tools_data['error']}")
                else:
                    print(f"\n⚠️  Unexpected response format: {tools_data}")
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON parse error: {e}")
        else:
            print("\n❌ No response received")
            stderr_output = process.stderr.read()
            if stderr_output:
                print(f"   Stderr: {stderr_output}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_mcp_with_proper_sequence()