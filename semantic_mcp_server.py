#!/usr/bin/env python3
"""
Semantic MCP Server - Python implementation
Interfaces with Cube.dev semantic layer for agentic AI platforms
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
        self.base_url = base_url or os.getenv("CUBE_API_URL", "http://localhost:4000")
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
        
        # Default measure if none specified
        if not query["measures"]:
            query["measures"].append("cities.count")
        
        # Clean up empty arrays
        query = {k: v for k, v in query.items() if v}
        
        return query


class AnalysisSuggester:
    """Generate analysis suggestions based on schema and business questions"""
    
    @staticmethod
    def get_common_analyses() -> List[Dict[str, Any]]:
        """Return common business analysis patterns"""
        return [
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
                "title": "Population by Region",
                "description": "Compare total population across different regions",
                "query": {
                    "measures": ["cities.total_population", "cities.count"],
                    "dimensions": ["cities.region"],
                    "order": {"cities.total_population": "desc"}
                }
            },
            {
                "title": "Population by State",
                "description": "Analyze population distribution by state",
                "query": {
                    "measures": ["cities.total_population", "cities.count"],
                    "dimensions": ["cities.state_name"],
                    "order": {"cities.total_population": "desc"}
                }
            },
            {
                "title": "Regional City Distribution",
                "description": "Count of cities in each region",
                "query": {
                    "measures": ["cities.count"],
                    "dimensions": ["cities.region"],
                    "order": {"cities.count": "desc"}
                }
            },
            {
                "title": "Top Cities by Population",
                "description": "Identify the most populous cities",
                "query": {
                    "measures": ["cities.total_population"],
                    "dimensions": ["cities.city_name", "cities.state_name"],
                    "order": {"cities.total_population": "desc"},
                    "limit": 5
                }
            },
            {
                "title": "State Population Rankings",
                "description": "Rank states by total population across all cities",
                "query": {
                    "measures": ["cities.total_population"],
                    "dimensions": ["cities.state_name"],
                    "order": {"cities.total_population": "desc"}
                }
            }
        ]
    
    @staticmethod
    def get_contextual_suggestions(business_question: str, meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate suggestions based on specific business question"""
        question_lower = business_question.lower()
        suggestions = []
        
        if any(word in question_lower for word in ["population", "demographic", "people"]):
            suggestions.extend([
                {
                    "title": "Population Analysis by Region",
                    "description": "Analyze population distribution across regions",
                    "query": {
                        "measures": ["cities.total_population"],
                        "dimensions": ["cities.region"],
                        "order": {"cities.total_population": "desc"}
                    }
                },
                {
                    "title": "Most Populous Cities",
                    "description": "Identify cities with highest population",
                    "query": {
                        "measures": ["cities.total_population"],
                        "dimensions": ["cities.city_name", "cities.state_name"],
                        "order": {"cities.total_population": "desc"},
                        "limit": 10
                    }
                }
            ])
        
        if any(word in question_lower for word in ["geography", "location", "geographic", "regional"]):
            suggestions.extend([
                {
                    "title": "Geographic Distribution",
                    "description": "Analyze data distribution across geographic regions",
                    "query": {
                        "measures": ["cities.count", "cities.total_population"],
                        "dimensions": ["cities.region", "cities.state_name"]
                    }
                },
                {
                    "title": "Regional Comparison",
                    "description": "Compare metrics across different regions",
                    "query": {
                        "measures": ["cities.total_population"],
                        "dimensions": ["cities.region"],
                        "order": {"cities.total_population": "desc"}
                    }
                }
            ])
        
        if any(word in question_lower for word in ["compare", "comparison", "ranking", "top"]):
            suggestions.extend([
                {
                    "title": "Top Performers",
                    "description": "Rank entities by key metrics",
                    "query": {
                        "measures": ["cities.total_population"],
                        "dimensions": ["cities.city_name"],
                        "order": {"cities.total_population": "desc"},
                        "limit": 10
                    }
                },
                {
                    "title": "State Rankings",
                    "description": "Compare performance across states",
                    "query": {
                        "measures": ["cities.total_population", "cities.count"],
                        "dimensions": ["cities.state_name"],
                        "order": {"cities.total_population": "desc"}
                    }
                }
            ])
        
        return suggestions


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
                description="Execute queries against the semantic layer using structured queries or natural language",
                inputSchema={
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
            ),
            Tool(
                name="get_schema_metadata",
                description="Get available cubes, dimensions, and measures from the semantic layer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "cube_name": {
                            "type": "string",
                            "description": "Optional: Get metadata for a specific cube"
                        }
                    }
                }
            ),
            Tool(
                name="suggest_analysis",
                description="Get suggestions for analysis based on available data and business questions",
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
            if "query" in arguments:
                # Direct structured query
                query = arguments["query"]
                result = await cube_client.query(query)
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(result, indent=2)
                        )
                    ]
                )
            
            elif "description" in arguments:
                # Natural language query
                description = arguments["description"]
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
            
            else:
                raise ValueError("Either 'query' or 'description' must be provided")
        
        elif name == "get_schema_metadata":
            meta = await cube_client.get_meta()
            
            if "cube_name" in arguments:
                cube_name = arguments["cube_name"]
                cubes = meta.get("cubes", [])
                cube = next((c for c in cubes if c.get("name") == cube_name), None)
                
                if not cube:
                    raise ValueError(f"Cube '{cube_name}' not found")
                
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(cube, indent=2)
                        )
                    ]
                )
            
            # Return full metadata
            return CallToolResult(
                content=[
                    TextContent(
                        type="text",
                        text=json.dumps(meta, indent=2)
                    )
                ]
            )
        
        elif name == "suggest_analysis":
            meta = await cube_client.get_meta()
            business_question = arguments.get("business_question", "")
            
            suggestions = {
                "common_analyses": AnalysisSuggester.get_common_analyses(),
                "available_cubes": [
                    {
                        "name": cube.get("name"),
                        "measures": [m.get("name") for m in cube.get("measures", [])],
                        "dimensions": [d.get("name") for d in cube.get("dimensions", [])]
                    }
                    for cube in meta.get("cubes", [])
                ]
            }
            
            if business_question:
                suggestions["contextual_suggestions"] = AnalysisSuggester.get_contextual_suggestions(
                    business_question, meta
                )
            
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