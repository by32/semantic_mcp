# Semantic MCP Server

A semantic layer built with DuckDB and Cube.dev that provides an MCP (Model Context Protocol) server for agentic AI platforms.

## Architecture

- **DuckDB**: High-performance analytical database
- **Cube.dev**: Semantic modeling framework with YAML configuration
- **MCP Server**: Protocol interface for AI agents to query the semantic layer

## Features

- 📊 **Rich Semantic Models**: Pre-defined business metrics and dimensions
- 🔍 **Natural Language Queries**: Convert business questions to structured queries
- 🚀 **High Performance**: DuckDB backend for fast analytical queries
- 🤖 **AI-Native**: Built specifically for agentic AI platform integration
- 📈 **Business Intelligence**: Sales, marketing, customer, and product analytics

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start the Semantic Layer
```bash
# Start Cube.dev with DuckDB backend
docker-compose up -d

# Wait for services to be ready
docker-compose logs -f
```

### 3. Initialize Data
```bash
# The docker-compose will automatically run init-data.sql
# To add synthetic data:
docker exec -it semantic_mcp-setup-data-1 duckdb /data/semantic.db < /scripts/generate-synthetic-data.sql
```

### 4. Setup and Run Python MCP Server
```bash
# Install Python dependencies
pip install -r requirements.txt

# Make server executable
chmod +x semantic_mcp_server.py

# Run the MCP server
./semantic_mcp_server.py
```

## Data Model

### Simple Dataset (Testing)
- **Cities**: 10 major US cities with population and geographic data
- **Sales**: 20 sample transactions across different product categories

### Complex Synthetic Dataset (Realistic Testing)
- **Companies**: 50 companies across 8 industries
- **Products**: 200 products with categories, subcategories, and brands
- **Customers**: 1,000 customers (Individual/Small Business/Enterprise)
- **Sales Reps**: 25 representatives with territories and performance tiers
- **Transactions**: 10,000 detailed sales transactions
- **Marketing**: 20 campaigns with performance tracking (600 data points)

## Semantic Models

### Sales Cube
- **Dimensions**: Date, Channel, Payment Method, Customer Type, Product Category, Geography, Sales Rep
- **Measures**: Total Revenue, Transaction Count, Quantity, Average Transaction Value, Discounts

### Products Cube
- **Dimensions**: Product Name, Category, Brand, Launch Date, Price Tier, Status
- **Measures**: Product Count, Average Price/Cost, Margin Analysis

### Customers Cube
- **Dimensions**: Customer Type, Registration Date, Geography, Credit Score Tier, Lifetime Value Tier
- **Measures**: Customer Count, Average Credit Score, Lifetime Value Analysis

### Marketing Cubes
- **Campaign Dimensions**: Channel, Target Region, Demographics, Duration
- **Performance Measures**: Impressions, Clicks, Conversions, CTR, Conversion Rate, ROAS

## MCP Tools

### 1. query_semantic_layer
Execute structured queries or natural language questions against the semantic layer.

**Structured Query Example:**
```json
{
  "measures": ["Sales.total_revenue", "Sales.total_transactions"],
  "dimensions": ["Sales.region", "Sales.product_category"],
  "order": {"Sales.total_revenue": "desc"}
}
```

**Natural Language Example:**
```json
{
  "description": "Show me monthly revenue by region"
}
```

### 2. get_schema_metadata
Get available cubes, dimensions, and measures.

### 3. suggest_analysis
Get analysis suggestions based on business questions.

## Usage Examples

### Connect to Cube.dev UI
- Open http://localhost:4000 for the Cube.dev playground
- **Note**: If you don't see cubes, there may be a DuckDB connectivity issue
- Check logs with: `docker-compose logs cube`

### Troubleshooting Schema Loading
If cubes don't appear in the UI:
1. Check database connectivity: `docker exec semantic_mcp-cube-1 ls -la /data/`
2. Verify schema files: `docker exec semantic_mcp-cube-1 ls -la /cube/conf/schema/`
3. Check Cube.dev logs: `docker-compose logs cube`

### Query via Postgres Interface (when working)
```bash
psql -h localhost -p 15432 -U root
```

### Sample Queries

**Regional Sales Performance:**
```json
{
  "measures": ["Sales.total_revenue", "Sales.unique_customers"],
  "dimensions": ["Sales.region"],
  "order": {"Sales.total_revenue": "desc"}
}
```

**Monthly Trend Analysis:**
```json
{
  "measures": ["Sales.total_revenue"],
  "timeDimensions": [{
    "dimension": "Sales.transaction_date",
    "granularity": "month"
  }]
}
```

**Product Category Performance:**
```json
{
  "measures": ["Sales.total_revenue", "Sales.total_quantity"],
  "dimensions": ["Sales.product_category", "Sales.brand"],
  "filters": [{
    "member": "Sales.transaction_date",
    "operator": "inDateRange",
    "values": ["2024-01-01", "2024-03-31"]
  }]
}
```

## Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Development Mode
```bash
python semantic_mcp_server.py
```

### Test Basic Functionality
```bash
# Test Cube.dev API directly
curl http://localhost:4000/cubejs-api/v1/meta

# Test with sample query
curl -X POST http://localhost:4000/cubejs-api/v1/load \
  -H "Content-Type: application/json" \
  -d '{"query": {"measures": ["Sales.total_revenue"], "dimensions": ["Sales.region"]}}'
```

## Configuration

### Environment Variables
- `CUBEJS_API_SECRET`: API secret for Cube.dev authentication
- `CUBEJS_DEV_MODE`: Enable development mode (default: true)
- `CUBEJS_DB_NAME`: DuckDB database path (default: /data/semantic.db)

### Custom Schema
Add new semantic models by creating YAML files in the `schema/` directory following Cube.dev conventions.

## Integration with AI Platforms

This MCP server is designed to work with agentic AI platforms that support the Model Context Protocol. The semantic layer provides a business-friendly interface for AI agents to:

1. **Understand Business Metrics**: Pre-defined KPIs and dimensions
2. **Execute Complex Analytics**: Multi-dimensional analysis with proper aggregations
3. **Generate Insights**: Business-context aware query suggestions
4. **Maintain Data Consistency**: Single source of truth for all metrics

## Troubleshooting

### Common Issues

1. **Docker Services Not Starting**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

2. **Database Connection Issues**
   ```bash
   docker-compose logs cube
   ```

3. **Schema Not Loading**
   - Check YAML syntax in schema files
   - Verify file permissions in schema directory

### Logs
```bash
# Cube.dev logs
docker-compose logs cube

# Database initialization logs
docker-compose logs setup-data
```