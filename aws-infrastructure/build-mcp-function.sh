#!/bin/bash
# Build MCP Server Lambda Function

set -e

echo "Building MCP Server Lambda Function..."

# Create function directory
mkdir -p mcp-function

# Create Lambda function
cat > mcp-function/lambda_function.py << 'EOF'
import json
import os
import boto3
from typing import Dict, Any

def lambda_handler(event, context):
    """
    MCP Server Lambda Function
    Handles MCP protocol requests via API Gateway
    """
    try:
        # Parse the request body
        body = event.get('body', '{}')
        if isinstance(body, str):
            request = json.loads(body)
        else:
            request = body
        
        method = request.get('method', '')
        request_id = request.get('id')
        
        # Initialize Lambda client for DuckDB queries
        lambda_client = boto3.client('lambda')
        duckdb_lambda_arn = os.environ['DUCKDB_LAMBDA_ARN']
        
        if method == 'initialize':
            return {
                'statusCode': 200,
                'body': json.dumps({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"experimental": {}, "tools": {"listChanged": False}},
                        "serverInfo": {"name": "aws-semantic-mcp", "version": "1.0.0"}
                    }
                })
            }
        
        elif method == 'tools/list':
            tools = [
                {
                    "name": "query_semantic_layer",
                    "description": "Execute business intelligence queries against S3 data lake",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Natural language description of what to analyze"
                            }
                        }
                    }
                }
            ]
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": tools}
                })
            }
        
        elif method == 'tools/call':
            params = request.get('params', {})
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name == 'query_semantic_layer':
                # Convert natural language to SQL
                description = arguments.get('description', '')
                sql_query = convert_to_sql(description)
                
                # Execute query via DuckDB Lambda
                response = lambda_client.invoke(
                    FunctionName=duckdb_lambda_arn,
                    Payload=json.dumps({'query': sql_query})
                )
                
                result = json.loads(response['Payload'].read())
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{
                                "type": "text",
                                "text": json.dumps({
                                    "natural_language": description,
                                    "sql_query": sql_query,
                                    "result": result
                                }, indent=2)
                            }]
                        }
                    })
                }
            
            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                    })
                }
        
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown method: {method}"}
                })
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                "jsonrpc": "2.0",
                "id": request.get('id') if 'request' in locals() else None,
                "error": {"code": -32603, "message": str(e)}
            })
        }

def convert_to_sql(description: str) -> str:
    """Convert natural language to SQL query"""
    desc_lower = description.lower()
    
    # Revenue queries
    if any(word in desc_lower for word in ['revenue', 'sales', 'product', 'category']):
        return """
            SELECT product_category, SUM(order_value) as total_revenue
            FROM sales 
            GROUP BY product_category 
            ORDER BY total_revenue DESC
            LIMIT 10
        """
    
    # Population queries
    elif any(word in desc_lower for word in ['population', 'city', 'cities']):
        return """
            SELECT city_name, population
            FROM cities 
            ORDER BY population DESC
            LIMIT 10
        """
    
    # Default query
    else:
        return "SELECT COUNT(*) as total_records FROM cities"
EOF

# Create deployment package
cd mcp-function
zip -r ../mcp-server.zip .
cd ..

# Cleanup
rm -rf mcp-function

echo "MCP function built successfully: mcp-server.zip"