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
        
        # Revenue and sales measures
        if any(word in desc_lower for word in ["revenue", "sales", "income"]):
            query["measures"].append("Sales.total_revenue")
        
        if "transaction" in desc_lower:
            query["measures"].append("Sales.total_transactions")
        
        if "customer" in desc_lower:
            query["measures"].append("Sales.unique_customers")
        
        if "quantity" in desc_lower or "units" in desc_lower:
            query["measures"].append("Sales.total_quantity")
        
        if "average" in desc_lower and "transaction" in desc_lower:
            query["measures"].append("Sales.average_transaction_value")
        
        # Dimension breakdowns
        if "region" in desc_lower:
            query["dimensions"].append("Sales.region")
        
        if "state" in desc_lower:
            query["dimensions"].append("Sales.state")
        
        if "category" in desc_lower or "product" in desc_lower:
            query["dimensions"].append("Sales.product_category")
        
        if "channel" in desc_lower:
            query["dimensions"].append("Sales.channel")
        
        if "brand" in desc_lower:
            query["dimensions"].append("Sales.brand")
        
        if "customer type" in desc_lower:
            query["dimensions"].append("Sales.customer_type")
        
        if "rep" in desc_lower or "salesperson" in desc_lower:
            query["dimensions"].append("Sales.sales_rep_name")
        
        # Time dimensions
        time_dim = None
        if "monthly" in desc_lower or "by month" in desc_lower:
            time_dim = {"dimension": "Sales.transaction_date", "granularity": "month"}
        elif "daily" in desc_lower or "by day" in desc_lower:
            time_dim = {"dimension": "Sales.transaction_date", "granularity": "day"}
        elif "yearly" in desc_lower or "by year" in desc_lower:
            time_dim = {"dimension": "Sales.transaction_date", "granularity": "year"}
        elif "weekly" in desc_lower or "by week" in desc_lower:
            time_dim = {"dimension": "Sales.transaction_date", "granularity": "week"}
        
        if time_dim:
            query["timeDimensions"] = [time_dim]
        
        # Ordering
        if "top" in desc_lower or "highest" in desc_lower:
            if query["measures"]:
                query["order"] = {query["measures"][0]: "desc"}
        elif "bottom" in desc_lower or "lowest" in desc_lower:
            if query["measures"]:
                query["order"] = {query["measures"][0]: "asc"}
        
        # Limits
        if "top 10" in desc_lower or "top ten" in desc_lower:
            query["limit"] = 10
        elif "top 5" in desc_lower or "top five" in desc_lower:
            query["limit"] = 5
        
        # Default measure if none specified
        if not query["measures"]:
            query["measures"].append("Sales.total_revenue")
        
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
                "title": "Sales Performance by Region",
                "description": "Compare revenue and transaction volume across different regions",
                "query": {
                    "measures": ["Sales.total_revenue", "Sales.total_transactions"],
                    "dimensions": ["Sales.region"],
                    "order": {"Sales.total_revenue": "desc"}
                }
            },
            {
                "title": "Top Products by Revenue",
                "description": "Identify best-performing product categories and brands",
                "query": {
                    "measures": ["Sales.total_revenue", "Sales.total_quantity"],
                    "dimensions": ["Sales.product_category", "Sales.brand"],
                    "order": {"Sales.total_revenue": "desc"},
                    "limit": 10
                }
            },
            {
                "title": "Monthly Sales Trend",
                "description": "Track revenue and transaction trends over time",
                "query": {
                    "measures": ["Sales.total_revenue", "Sales.average_transaction_value"],
                    "timeDimensions": [{
                        "dimension": "Sales.transaction_date",
                        "granularity": "month"
                    }]
                }
            },
            {
                "title": "Customer Segmentation Analysis",
                "description": "Analyze revenue by customer type and geographic distribution",
                "query": {
                    "measures": ["Sales.total_revenue", "Sales.unique_customers"],
                    "dimensions": ["Sales.customer_type", "Sales.region"]
                }
            },
            {
                "title": "Sales Rep Performance",
                "description": "Compare sales representative performance and productivity",
                "query": {
                    "measures": ["Sales.total_revenue", "Sales.total_transactions"],
                    "dimensions": ["Sales.sales_rep_name", "Sales.rep_performance_tier"],
                    "order": {"Sales.total_revenue": "desc"}
                }
            },
            {
                "title": "Channel Effectiveness",
                "description": "Compare performance across different sales channels",
                "query": {
                    "measures": ["Sales.total_revenue", "Sales.average_transaction_value"],
                    "dimensions": ["Sales.channel"],
                    "order": {"Sales.total_revenue": "desc"}
                }
            }
        ]
    
    @staticmethod
    def get_contextual_suggestions(business_question: str, meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate suggestions based on specific business question"""
        question_lower = business_question.lower()
        suggestions = []
        
        if any(word in question_lower for word in ["marketing", "campaign", "advertising"]):
            suggestions.extend([
                {
                    "title": "Marketing Campaign ROI",
                    "description": "Analyze return on advertising spend by campaign channel",
                    "query": {
                        "measures": ["CampaignPerformance.total_revenue", "CampaignPerformance.return_on_ad_spend"],
                        "dimensions": ["CampaignPerformance.campaign_channel"]
                    }
                },
                {
                    "title": "Campaign Performance Metrics",
                    "description": "Track key performance indicators for marketing campaigns",
                    "query": {
                        "measures": ["CampaignPerformance.click_through_rate", "CampaignPerformance.conversion_rate"],
                        "dimensions": ["CampaignPerformance.campaign_name"]
                    }
                }
            ])
        
        if any(word in question_lower for word in ["customer", "retention", "loyalty"]):
            suggestions.extend([
                {
                    "title": "Customer Lifetime Value Analysis",
                    "description": "Analyze customer value by type and credit score",
                    "query": {
                        "measures": ["Customers.average_lifetime_value", "Customers.total_customers"],
                        "dimensions": ["Customers.customer_type", "Customers.credit_score_tier"]
                    }
                },
                {
                    "title": "Geographic Customer Distribution",
                    "description": "Map customer distribution across regions",
                    "query": {
                        "measures": ["Customers.total_customers"],
                        "dimensions": ["Customers.region", "Customers.customer_type"]
                    }
                }
            ])
        
        if any(word in question_lower for word in ["product", "inventory", "catalog"]):
            suggestions.extend([
                {
                    "title": "Product Profitability Analysis",
                    "description": "Compare profit margins across product categories",
                    "query": {
                        "measures": ["Products.average_margin", "Products.total_products"],
                        "dimensions": ["Products.category", "Products.price_tier"]
                    }
                },
                {
                    "title": "Product Portfolio Health",
                    "description": "Analyze active vs discontinued products",
                    "query": {
                        "measures": ["Products.total_products", "Products.average_unit_price"],
                        "dimensions": ["Products.is_active", "Products.category"]
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