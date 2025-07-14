#!/usr/bin/env python3
"""Test edge cases that might cause LangFlow errors"""

import subprocess
import json

def test_edge_cases():
    print("🧪 Testing Edge Cases for LangFlow Issues")
    print("=" * 45)
    
    process = subprocess.Popen(
        ['python3', '/Users/byoungs/Documents/gitlab/semantic_mcp/langflow_mcp_server.py'],
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
                "clientInfo": {"name": "langflow-test", "version": "1.0.0"}
            },
            "id": 1
        }
        
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        init_response = process.stdout.readline().strip()
        
        # Send initialized
        initialized = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized", 
            "params": {}
        }
        process.stdin.write(json.dumps(initialized) + '\n')
        process.stdin.flush()
        
        # Test cases that might cause issues
        test_cases = [
            {"description": ""},  # Empty description
            {"description": "hello"},  # Non-business query
            {"description": "show me something"},  # Vague query
            {"description": "revenue by product category"},  # Exact match
            {},  # No description at all
        ]
        
        for i, args in enumerate(test_cases, 3):
            print(f"{i}️⃣  Testing with args: {args}")
            
            test_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "query_semantic_layer",
                    "arguments": args
                },
                "id": i
            }
            
            process.stdin.write(json.dumps(test_request) + '\n')
            process.stdin.flush()
            
            response = process.stdout.readline().strip()
            if response:
                try:
                    data = json.loads(response)
                    if "error" in data:
                        print(f"   ❌ Error: {data['error']['message']}")
                        if "data" in data["error"]:
                            print(f"   🔍 Details: {data['error']['data']['error']}")
                    else:
                        print(f"   ✅ Success: Got response")
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response")
            else:
                print(f"   ❌ No response")
        
        # Check stderr for debug messages
        stderr_output = ""
        try:
            process.stderr.flush()
            # Try to read any available stderr without blocking
            import select
            import sys
            if select.select([process.stderr], [], [], 0)[0]:
                stderr_output = process.stderr.read()
        except:
            pass
            
        if stderr_output:
            print(f"\n🔍 Debug output:\n{stderr_output}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_edge_cases()