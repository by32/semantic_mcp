#!/usr/bin/env python3
"""
LangFlow-compatible MCP Server with real Cube.js data
Works with LangFlow Desktop app - no Docker dependencies for the server itself
"""

import asyncio
import json
import sys
import os
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin
import urllib.request
import urllib.parse
import urllib.error

class CubeAPIClient:
    """HTTP client for Cube.js API using only standard library"""
    
    def __init__(self, base_url: Optional[str] = None, api_token: Optional[str] = None):
        self.base_url = base_url or "http://localhost:4000"
        self.api_token = api_token or os.getenv("CUBE_API_SECRET")
    
    def query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a query against Cube.js"""
        url = urljoin(self.base_url, "/cubejs-api/v1/load")
        
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        data = json.dumps({"query": query}).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            # Read the error response body for more details
            error_body = e.read().decode('utf-8') if e.fp else "No error details"
            raise Exception(f"Cube.js HTTP Error {e.code}: {e.reason}. Response: {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Failed to connect to Cube.js: {e}")
    
    def get_meta(self) -> Dict[str, Any]:
        """Get metadata about available cubes, dimensions, and measures"""
        url = urljoin(self.base_url, "/cubejs-api/v1/meta")
        
        headers = {}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            # Read the error response body for more details
            error_body = e.read().decode('utf-8') if e.fp else "No error details"
            raise Exception(f"Cube.js metadata HTTP Error {e.code}: {e.reason}. Response: {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Failed to get metadata from Cube.js: {e}")

class NaturalLanguageProcessor:
    """Convert natural language to Cube.js queries"""
    
    @staticmethod
    def convert_to_query(description: str) -> Dict[str, Any]:
        """Convert natural language description to Cube.js query"""
        if not description or not description.strip():
            # Handle empty descriptions
            return {
                "measures": ["cities.count"],
                "dimensions": ["cities.city_name"],
                "limit": 5
            }
            
        desc_lower = description.lower().strip()
        query = {
            "measures": [],
            "dimensions": [],
            "filters": []
        }
        
        # Cities measures
        if any(word in desc_lower for word in ["population", "people", "residents"]):
            query["measures"].append("cities.total_population")
        
        if any(word in desc_lower for word in ["count", "number", "how many"]) and any(word in desc_lower for word in ["cities", "city"]):
            query["measures"].append("cities.count")
        
        # Cities dimensions
        if "city" in desc_lower and ("name" in desc_lower or "cities" in desc_lower):
            query["dimensions"].append("cities.city_name")
        
        if "state" in desc_lower and not any(word in desc_lower for word in ["customer", "sales"]):
            query["dimensions"].append("cities.state_name")
        
        if "region" in desc_lower and not any(word in desc_lower for word in ["customer", "sales"]):
            query["dimensions"].append("cities.region")
        
        # Sales measures
        if any(word in desc_lower for word in ["revenue", "sales", "income", "money"]):
            query["measures"].append("sales.total_revenue")
        
        if any(word in desc_lower for word in ["order", "average order", "aov"]):
            query["measures"].append("sales.average_order_value")
        
        if any(word in desc_lower for word in ["quantity", "volume", "units"]):
            query["measures"].append("sales.total_quantity")
        
        if any(word in desc_lower for word in ["discount", "discounts"]):
            query["measures"].append("sales.total_discount_amount")
        
        # Sales dimensions
        if any(word in desc_lower for word in ["category", "product"]):
            query["dimensions"].append("sales.product_category")
        
        if any(word in desc_lower for word in ["channel", "channels"]):
            query["dimensions"].append("sales.channel")
        
        if any(word in desc_lower for word in ["payment", "payment method"]):
            query["dimensions"].append("sales.payment_method")
        
        if any(word in desc_lower for word in ["discount tier", "discount level"]):
            query["dimensions"].append("sales.discount_tier")
        
        # Customer measures
        if any(word in desc_lower for word in ["customer", "customers"]) and any(word in desc_lower for word in ["count", "number"]):
            query["measures"].append("customers.count")
        
        if any(word in desc_lower for word in ["lifetime value", "ltv", "customer value"]):
            query["measures"].append("customers.average_lifetime_value")
        
        if any(word in desc_lower for word in ["credit score", "credit"]):
            query["measures"].append("customers.average_credit_score")
        
        # Customer dimensions
        if any(word in desc_lower for word in ["customer type", "customer segment"]):
            query["dimensions"].append("customers.customer_type")
        
        if any(word in desc_lower for word in ["credit score tier", "credit tier"]):
            query["dimensions"].append("customers.credit_score_tier")
        
        # Ordering
        if "top" in desc_lower or "highest" in desc_lower or "largest" in desc_lower:
            if query["measures"]:
                query["order"] = {query["measures"][0]: "desc"}
        elif "bottom" in desc_lower or "lowest" in desc_lower or "smallest" in desc_lower:
            if query["measures"]:
                query["order"] = {query["measures"][0]: "asc"}
        
        # Limits
        if "top 10" in desc_lower or "top ten" in desc_lower:
            query["limit"] = 10
        elif "top 5" in desc_lower or "top five" in desc_lower:
            query["limit"] = 5
        elif "top 3" in desc_lower or "top three" in desc_lower:
            query["limit"] = 3
        
        # Clean up empty arrays first
        query = {k: v for k, v in query.items() if v}
        
        # CRITICAL: Ensure we always have at least measures or dimensions
        # Cube.js requires at least one of: measures, dimensions, or timeDimensions
        if not query.get("measures") and not query.get("dimensions"):
            # Default to a safe query based on description content
            if any(word in desc_lower for word in ["sales", "revenue", "product", "category"]):
                query = {
                    "measures": ["sales.total_revenue"],
                    "dimensions": ["sales.product_category"],
                    "order": {"sales.total_revenue": "desc"},
                    "limit": 5
                }
            elif any(word in desc_lower for word in ["customer", "customers", "client"]):
                query = {
                    "measures": ["customers.count"],
                    "dimensions": ["customers.customer_type"],
                    "limit": 5
                }
            else:
                # Default to cities
                query = {
                    "measures": ["cities.count"],
                    "dimensions": ["cities.city_name"],
                    "limit": 5
                }
        
        # Double-check that we have valid content
        if not query.get("measures") and not query.get("dimensions"):
            # Fallback safety net
            query["measures"] = ["cities.count"]
        
        return query

class LangFlowMCPServer:
    """MCP Server optimized for LangFlow Desktop"""
    
    def __init__(self):
        self.cube_client = CubeAPIClient()
        self.tools = [
            {
                "name": "query_semantic_layer",
                "description": "Execute queries against the semantic layer using structured queries or natural language",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "object",
                            "description": "Structured Cube.dev query with measures, dimensions, filters, etc."
                        },
                        "description": {
                            "type": "string",
                            "description": "Natural language description of what you want to analyze"
                        }
                    },
                    "anyOf": [
                        {"required": ["query"]},
                        {"required": ["description"]}
                    ]
                }
            },
            {
                "name": "get_schema_metadata",
                "description": "Get available cubes, dimensions, and measures from the semantic layer",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "cube_name": {
                            "type": "string",
                            "description": "Optional: Get metadata for a specific cube"
                        }
                    }
                }
            },
            {
                "name": "suggest_analysis",
                "description": "Get suggestions for analysis based on available data and business questions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "business_question": {
                            "type": "string",
                            "description": "Business question or area of interest"
                        }
                    }
                }
            }
        ]
    
    def handle_request(self, request_str: str) -> str:
        """Handle incoming MCP requests"""
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
                            "name": "langflow-semantic-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
                return json.dumps(response)
            
            elif method == "notifications/initialized":
                return ""  # No response for notifications
            
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
                return self._handle_tool_call(request)
            
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
    
    def _handle_tool_call(self, request: Dict[str, Any]) -> str:
        """Handle tool call requests"""
        try:
            params = request.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            request_id = request.get("id")
            
            if tool_name == "query_semantic_layer":
                if "query" in arguments:
                    # Direct structured query
                    query = arguments["query"]
                    result = self.cube_client.query(query)
                    
                    response_text = json.dumps(result, indent=2)
                    
                elif "description" in arguments:
                    # Natural language query
                    description = arguments["description"]
                    query = NaturalLanguageProcessor.convert_to_query(description)
                    
                    # Debug: Log the generated query
                    import sys
                    print(f"DEBUG: Generated query for '{description}': {query}", file=sys.stderr)
                    
                    result = self.cube_client.query(query)
                    
                    response_data = {
                        "natural_language": description,
                        "generated_query": query,
                        "result": result
                    }
                    
                    response_text = json.dumps(response_data, indent=2)
                    
                else:
                    raise ValueError("Either 'query' or 'description' must be provided")
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": response_text
                        }]
                    }
                }
                return json.dumps(response)
            
            elif tool_name == "get_schema_metadata":
                meta = self.cube_client.get_meta()
                
                if "cube_name" in arguments:
                    cube_name = arguments["cube_name"]
                    cubes = meta.get("cubes", [])
                    cube = next((c for c in cubes if c.get("name") == cube_name), None)
                    
                    if not cube:
                        raise ValueError(f"Cube '{cube_name}' not found")
                    
                    response_text = json.dumps(cube, indent=2)
                else:
                    response_text = json.dumps(meta, indent=2)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": response_text
                        }]
                    }
                }
                return json.dumps(response)
            
            elif tool_name == "suggest_analysis":
                # Get real metadata for suggestions
                meta = self.cube_client.get_meta()
                business_question = arguments.get("business_question", "")
                
                suggestions = {
                    "common_analyses": [
                        {
                            "title": "Revenue by Product Category",
                            "description": "Analyze sales revenue across different product categories",
                            "query": {
                                "measures": ["sales.total_revenue"],
                                "dimensions": ["sales.product_category"],
                                "order": {"sales.total_revenue": "desc"}
                            }
                        },
                        {
                            "title": "Cities by Population",
                            "description": "Compare cities by total population",
                            "query": {
                                "measures": ["cities.total_population"],
                                "dimensions": ["cities.city_name"],
                                "order": {"cities.total_population": "desc"},
                                "limit": 10
                            }
                        },
                        {
                            "title": "Customer Lifetime Value by Type",
                            "description": "Analyze customer value across different segments",
                            "query": {
                                "measures": ["customers.average_lifetime_value", "customers.count"],
                                "dimensions": ["customers.customer_type"],
                                "order": {"customers.average_lifetime_value": "desc"}
                            }
                        }
                    ],
                    "available_cubes": [
                        {
                            "name": cube.get("name"),
                            "measures": [m.get("name") for m in cube.get("measures", [])],
                            "dimensions": [d.get("name") for d in cube.get("dimensions", [])]
                        }
                        for cube in meta.get("cubes", [])
                    ]
                }
                
                response_text = json.dumps(suggestions, indent=2)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": response_text
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
                
        except Exception as e:
            # Enhanced error logging for debugging
            import traceback
            error_details = {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "request": request if 'request' in locals() else None
            }
            
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution error: {str(e)}",
                    "data": error_details
                }
            }
            return json.dumps(response)

def main():
    """Main entry point"""
    server = LangFlowMCPServer()
    
    # Process stdin line by line
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        response = server.handle_request(line)
        if response:  # Don't output empty responses
            print(response)
            sys.stdout.flush()

if __name__ == "__main__":
    main()