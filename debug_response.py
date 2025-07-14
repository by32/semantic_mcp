#!/usr/bin/env python3
"""Debug the actual response structure"""

import subprocess
import json

def debug_response():
    process = subprocess.Popen(
        ['/Users/byoungs/Documents/gitlab/semantic_mcp/scripts/langflow-mcp-wrapper.sh'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Initialize
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0.0"}
            },
            "id": 1
        }
        
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        init_response = process.stdout.readline().strip()
        
        # Send initialized
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        process.stdin.write(json.dumps(initialized_notification) + '\n')
        process.stdin.flush()
        
        # Test query
        nl_request = {
            "jsonrpc": "2.0",
            "method": "tools/call", 
            "params": {
                "name": "query_semantic_layer",
                "arguments": {
                    "description": "Show me the top 5 cities by population"
                }
            },
            "id": 2
        }
        
        process.stdin.write(json.dumps(nl_request) + '\n')
        process.stdin.flush()
        
        response = process.stdout.readline().strip()
        print("Raw Response:")
        print(response)
        
        print("\nParsed Response:")
        data = json.loads(response)
        print(json.dumps(data, indent=2))
        
        print("\nResult Content:")
        result = data["result"]
        print(json.dumps(result, indent=2))
        
        print("\nContent Text:")
        content_text = result["content"][0]["text"]
        print(content_text)
        
        print("\nParsed Content:")
        content_data = json.loads(content_text)
        print(json.dumps(content_data, indent=2))
        
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    debug_response()