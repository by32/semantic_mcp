#!/usr/bin/env python3
"""Test MCP connection to verify wrapper script works correctly"""

import subprocess
import json
import sys

def test_mcp_connection():
    # Start the MCP server via wrapper script
    process = subprocess.Popen(
        ['/Users/byoungs/Documents/gitlab/semantic_mcp/scripts/langflow-mcp-wrapper.sh'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Send initialization
        init_msg = {
            "jsonrpc": "2.0",
            "method": "initialize", 
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            },
            "id": 1
        }
        
        print("Sending initialization...")
        process.stdin.write(json.dumps(init_msg) + '\n')
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Init response: {response.strip()}")
        
        # Send tools/list
        tools_msg = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        print("Requesting tools list...")
        process.stdin.write(json.dumps(tools_msg) + '\n')
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        print(f"Tools response: {response.strip()}")
        
        # Parse and show tools
        try:
            tools_data = json.loads(response.strip())
            if "result" in tools_data and "tools" in tools_data["result"]:
                tools = tools_data["result"]["tools"]
                print(f"\nFound {len(tools)} MCP tools:")
                for tool in tools:
                    print(f"  - {tool['name']}: {tool.get('description', 'No description')}")
            else:
                print("No tools found in response")
        except json.JSONDecodeError:
            print("Could not parse tools response as JSON")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_mcp_connection()