#!/usr/bin/env python3
"""Comprehensive MCP server test to identify any remaining issues"""

import subprocess
import json
import time
import sys

def test_mcp_tool_call():
    """Test the complete MCP workflow including tool calls"""
    
    print("🧪 Comprehensive MCP Server Test")
    print("=" * 50)
    
    # Start the MCP server
    process = subprocess.Popen(
        ['/Users/byoungs/Documents/gitlab/semantic_mcp/scripts/langflow-mcp-wrapper.sh'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Step 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "langflow-test",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        print("1️⃣  Testing initialize...")
        process.stdin.write(json.dumps(init_request) + '\n')
        process.stdin.flush()
        
        init_response = process.stdout.readline().strip()
        print(f"   ✅ Response: {init_response[:100]}...")
        
        if not init_response:
            stderr_output = process.stderr.read()
            print(f"   ❌ No response. Stderr: {stderr_output}")
            return False
        
        # Step 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        print("2️⃣  Sending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification) + '\n')
        process.stdin.flush()
        time.sleep(0.2)
        
        # Step 3: List tools
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        print("3️⃣  Testing tools/list...")
        process.stdin.write(json.dumps(tools_request) + '\n')
        process.stdin.flush()
        
        tools_response = process.stdout.readline().strip()
        print(f"   ✅ Response: {tools_response[:100]}...")
        
        # Parse tools
        tools_data = json.loads(tools_response)
        if "result" not in tools_data or "tools" not in tools_data["result"]:
            print(f"   ❌ Invalid tools response: {tools_data}")
            return False
        
        tools = tools_data["result"]["tools"]
        print(f"   ✅ Found {len(tools)} tools")
        
        # Step 4: Test tool call - get schema metadata (simplest)
        schema_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_schema_metadata",
                "arguments": {}
            },
            "id": 3
        }
        
        print("4️⃣  Testing tools/call (get_schema_metadata)...")
        process.stdin.write(json.dumps(schema_request) + '\n')
        process.stdin.flush()
        
        schema_response = process.stdout.readline().strip()
        print(f"   ✅ Response: {schema_response[:100]}...")
        
        # Parse schema response
        try:
            schema_data = json.loads(schema_response)
            if "result" in schema_data:
                print("   ✅ Schema call successful")
                # Check if result has expected structure
                result = schema_data["result"]
                if "content" in result and isinstance(result["content"], list):
                    print("   ✅ Response format is correct")
                else:
                    print(f"   ⚠️  Unexpected result format: {result}")
            elif "error" in schema_data:
                print(f"   ❌ Schema call error: {schema_data['error']}")
                return False
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parse error: {e}")
            return False
        
        # Step 5: Test natural language query
        nl_request = {
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
        
        print("5️⃣  Testing natural language query...")
        process.stdin.write(json.dumps(nl_request) + '\n')
        process.stdin.flush()
        
        nl_response = process.stdout.readline().strip()
        print(f"   ✅ Response: {nl_response[:100]}...")
        
        # Parse NL response
        try:
            nl_data = json.loads(nl_response)
            if "result" in nl_data:
                print("   ✅ Natural language query successful")
                result = nl_data["result"]
                if "content" in result and isinstance(result["content"], list):
                    print("   ✅ Response format is correct")
                    # Try to parse the content
                    content_text = result["content"][0]["text"]
                    content_data = json.loads(content_text)
                    if "natural_language" in content_data and "generated_query" in content_data:
                        print("   ✅ Content structure is correct")
                        print(f"   📝 Generated query: {content_data['generated_query']}")
                    else:
                        print(f"   ⚠️  Unexpected content structure: {list(content_data.keys())}")
                else:
                    print(f"   ⚠️  Unexpected result format: {result}")
            elif "error" in nl_data:
                print(f"   ❌ Natural language query error: {nl_data['error']}")
                return False
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parse error: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Content parsing error: {e}")
            return False
        
        print("\n🎉 ALL TESTS PASSED!")
        print("The MCP server is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test exception: {e}")
        stderr_output = process.stderr.read()
        if stderr_output:
            print(f"Stderr: {stderr_output}")
        return False
    finally:
        process.terminate()
        process.wait()

def test_direct_docker_exec():
    """Test direct docker exec without wrapper script"""
    print("\n🔧 Testing direct docker exec...")
    
    process = subprocess.Popen(
        ['docker', 'exec', '-i', 'semantic_mcp-mcp-server-1', 'python', '/app/semantic_mcp_server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Quick initialization test
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
        
        response = process.stdout.readline().strip()
        if response:
            print(f"   ✅ Direct docker exec works: {response[:50]}...")
            return True
        else:
            stderr_output = process.stderr.read()
            print(f"   ❌ Direct docker exec failed. Stderr: {stderr_output}")
            return False
            
    except Exception as e:
        print(f"   ❌ Direct docker exec exception: {e}")
        return False
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    success = test_mcp_tool_call()
    test_direct_docker_exec()
    
    if success:
        print("\n✅ MCP server is ready for LangFlow!")
        print("Use this command in LangFlow MCP Tools:")
        print("/Users/byoungs/Documents/gitlab/semantic_mcp/scripts/langflow-mcp-wrapper.sh")
    else:
        print("\n❌ MCP server has issues that need to be fixed.")
        sys.exit(1)