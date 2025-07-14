#!/usr/bin/env python3
"""
Standalone MCP Server for LangFlow Desktop App Testing
This version doesn't require Docker and works with mock data
"""

import asyncio
import json
import sys
from typing import Any, Dict

# Simple MCP server implementation without external dependencies
class SimpleMCPServer:
    def __init__(self):
        self.tools = [
            {
                "name": "query_semantic_layer",
                "description": "Execute natural language queries against business data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Natural language description of what you want to analyze"
                        }
                    },
                    "required": ["description"]
                }
            },
            {
                "name": "get_schema_metadata", 
                "description": "Get available data cubes and dimensions",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    def handle_request(self, request_str: str) -> str:
        try:
            request = json.loads(request_str)
            method = request.get("method")
            request_id = request.get("id")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "experimental": {},
                            "tools": {"listChanged": False}
                        },
                        "serverInfo": {
                            "name": "standalone-semantic-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
                return json.dumps(response)
            
            elif method == "notifications/initialized":
                # No response needed for notifications
                return ""
            
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": self.tools
                    }
                }
                return json.dumps(response)
            
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "query_semantic_layer":
                    description = arguments.get("description", "")
                    
                    # Mock response with sample data
                    mock_result = {
                        "natural_language": description,
                        "generated_query": {
                            "measures": ["cities.total_population"],
                            "dimensions": ["cities.city_name"],
                            "order": {"cities.total_population": "desc"},
                            "limit": 5
                        },
                        "result": {
                            "data": [
                                {"cities.city_name": "New York", "cities.total_population": "8336817"},
                                {"cities.city_name": "Los Angeles", "cities.total_population": "3979576"},
                                {"cities.city_name": "Chicago", "cities.total_population": "2693976"},
                                {"cities.city_name": "Houston", "cities.total_population": "2320268"},
                                {"cities.city_name": "Phoenix", "cities.total_population": "1680992"}
                            ]
                        }
                    }
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{
                                "type": "text",
                                "text": json.dumps(mock_result, indent=2)
                            }]
                        }
                    }
                    return json.dumps(response)
                
                elif tool_name == "get_schema_metadata":
                    mock_schema = {
                        "cubes": [
                            {
                                "name": "cities",
                                "measures": ["count", "total_population"],
                                "dimensions": ["city_name", "state_name", "region"]
                            },
                            {
                                "name": "sales", 
                                "measures": ["total_revenue", "count"],
                                "dimensions": ["product_category", "channel"]
                            }
                        ]
                    }
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{
                                "type": "text",
                                "text": json.dumps(mock_schema, indent=2)
                            }]
                        }
                    }
                    return json.dumps(response)
                
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Unknown tool: {tool_name}"
                        }
                    }
                    return json.dumps(response)
            
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown method: {method}"
                    }
                }
                return json.dumps(response)
                
        except Exception as e:
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            return json.dumps(response)

def main():
    server = SimpleMCPServer()
    
    # Process stdin line by line
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        response = server.handle_request(line)
        if response:  # Don't output empty responses (for notifications)
            print(response)
            sys.stdout.flush()

if __name__ == "__main__":
    main()