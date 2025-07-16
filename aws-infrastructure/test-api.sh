#!/bin/bash
# Test the deployed AWS API

set -e

echo "🧪 Testing AWS MCP API..."

# Get API Gateway URL
API_URL=$(terraform output -raw api_gateway_url)

if [ -z "$API_URL" ]; then
    echo "❌ Could not get API Gateway URL from Terraform"
    exit 1
fi

echo "Testing API at: $API_URL"

# Test 1: Initialize
echo "1. Testing initialize..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test", "version": "1.0.0"}
    },
    "id": 1
  }' | jq .

# Test 2: List tools
echo "2. Testing tools/list..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 2
  }' | jq .

# Test 3: Query semantic layer
echo "3. Testing query_semantic_layer..."
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "query_semantic_layer",
      "arguments": {
        "description": "Show me revenue by product category"
      }
    },
    "id": 3
  }' | jq .

echo "✅ API testing complete!"