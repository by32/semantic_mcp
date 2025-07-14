#!/usr/bin/env python3
"""
Local Semantic MCP Server - connects to containerized Cube.js
"""

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult,
)
from pydantic import BaseModel, Field


class CubeQuery(BaseModel):
    """Cube.dev query structure"""
    measures: Optional[List[str]] = Field(default_factory=list)
    dimensions: Optional[List[str]] = Field(default_factory=list)
    timeDimensions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    filters: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    order: Optional[Dict[str, str]] = Field(default_factory=dict)
    limit: Optional[int] = None


class CubeAPIClient:
    """Client for Cube.dev REST API"""
    
    def __init__(self, base_url: Optional[str] = None, api_token: Optional[str] = None):
        # Connect to containerized Cube.js from host machine
        self.base_url = base_url or "http://localhost:4000"
        self.api_token = api_token or os.getenv("CUBE_API_SECRET")
        self.client = httpx.AsyncClient()
    
    async def query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a query against Cube.dev"""
        url = urljoin(self.base_url, "/cubejs-api/v1/load")
        headers = {"Content-Type": "application/json"}
        
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        response = await self.client.post(
            url,
            json={"query": query},
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    async def get_meta(self) -> Dict[str, Any]:
        """Get metadata about available cubes, dimensions, and measures"""
        url = urljoin(self.base_url, "/cubejs-api/v1/meta")
        headers = {}
        
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        response = await self.client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


class NaturalLanguageProcessor:
    """Simple natural language to Cube.dev query converter"""
    
    @staticmethod
    def convert_to_query(description: str) -> Dict[str, Any]:
        """Convert natural language description to Cube.dev query"""
        desc_lower = description.lower()
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
        if "city" in desc_lower and "name" in desc_lower:
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
        
        # Sales dimensions
        if any(word in desc_lower for word in ["category", "product"]):
            query["dimensions"].append("sales.product_category")
        
        # Customer measures
        if any(word in desc_lower for word in ["customer", "customers"]) and any(word in desc_lower for word in ["count", "number"]):
            query["measures"].append("customers.count")
        
        if any(word in desc_lower for word in ["lifetime value", "ltv", "customer value"]):
            query["measures"].append("customers.average_lifetime_value")
        
        # Customer dimensions
        if any(word in desc_lower for word in ["customer type", "customer segment"]):
            query["dimensions"].append("customers.customer_type")
        
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
        
        # Default measure if none specified
        if not query["measures"]:
            query["measures"].append("cities.count")
        
        # Clean up empty arrays
        query = {k: v for k, v in query.items() if v}
        
        return query


# Initialize the MCP server
server = Server("semantic-mcp")

# Initialize Cube.dev client
cube_client = CubeAPIClient()


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools for the semantic layer"""
    return ListToolsResult(
        tools=[
            Tool(
                name="query_semantic_layer",
                description="Execute queries against the semantic layer using natural language",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "Natural language description of what you want to analyze"
                        }
                    },
                    "required": ["description"]
                }
            ),
            Tool(
                name="get_schema_metadata",
                description="Get available cubes, dimensions, and measures",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            Tool(
                name="suggest_analysis",
                description="Get analysis suggestions",
                inputSchema={
                    "type": "object", 
                    "properties": {
                        "business_question": {
                            "type": "string",
                            "description": "Business question or area of interest"
                        }
                    }
                }
            )
        ]
    )


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls"""
    try:
        if name == "query_semantic_layer":
            description = arguments.get("description", "")
            query = NaturalLanguageProcessor.convert_to_query(description)
            result = await cube_client.query(query)
            
            response = {
                "natural_language": description,
                "generated_query": query,
                "result": result
            }
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(response, indent=2)
                    )
                ]
            )
        
        elif name == "get_schema_metadata":
            meta = await cube_client.get_meta()
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(meta, indent=2)
                    )
                ]
            )
        
        elif name == "suggest_analysis":
            suggestions = {
                "common_analyses": [
                    {
                        "title": "Cities by Population",
                        "description": "Compare cities by total population"
                    },
                    {
                        "title": "Sales by Category", 
                        "description": "Analyze revenue by product category"
                    }
                ]
            }
            
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(suggestions, indent=2)
                    )
                ]
            )
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ],
            isError=True
        )


async def main():
    """Main entry point for the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.run(cube_client.close())