# Semantic MCP Server

A complete DuckLake semantic layer implementation with MinIO object storage, DuckDB analytics engine, and Cube.dev business semantics, providing an MCP (Model Context Protocol) server for agentic AI platforms.

## Architecture

### DuckLake Implementation
- **MinIO Object Storage**: S3-compatible storage for Parquet data lake files
- **DuckDB Query Engine**: High-performance analytical database with S3 integration
- **Cube.dev Semantic Layer**: Business-friendly metric definitions and YAML models
- **MCP Server**: Model Context Protocol interface for AI agent integration

### Data Flow
```
Sample Data → MinIO Parquet Files (Data Lake)
                    ↓
             DuckDB Tables (Query Engine) 
                    ↓
            Cube.js Semantic Layer (Business Logic)
                    ↓
           MCP Server (AI Agent Interface)
```

This architecture provides true separation of storage and compute, enabling scalable analytics with object storage economics and fast query performance.

## Features

- 🏗️ **DuckLake Architecture**: Modern data lake with MinIO object storage + DuckDB analytics
- 📊 **Rich Semantic Models**: Business-friendly metric definitions across sales, customers, and geographic data
- 🔍 **Natural Language Queries**: Convert business questions to structured insights automatically
- 🚀 **High Performance**: Sub-15ms query response times with columnar analytics
- 🤖 **AI-Native**: Built specifically for agentic AI platform integration via MCP protocol
- 📈 **Business Intelligence**: Complete demo with 11 test scenarios across 7 business categories
- ⚡ **Proven Performance**: 100% test success rate with comprehensive validation suite

## Quick Start

### Option A: Local Development Setup

#### 1. Start the DuckLake Stack
```bash
# Start complete DuckLake architecture: MinIO + DuckDB + Cube.js + MCP
docker-compose -f docker-compose-lake.yml up -d

# Wait for services to be ready (MinIO, DuckDB setup, Cube.js)
docker-compose -f docker-compose-lake.yml logs -f
```

#### 2. Verify Data Lake Setup
```bash
# Check that all services are healthy
docker-compose -f docker-compose-lake.yml ps

# Test Cube.js API
curl http://localhost:4000/cubejs-api/v1/meta

# Verify MinIO storage (optional)
# Access MinIO console at http://localhost:9001 (admin/password123)
```

#### 3. Run Comprehensive Demo
```bash
# Install Python dependencies with uv
uv init && uv add httpx

# Execute the complete test suite
uv run python demo_test_suite.py
```

#### 4. LangFlow Integration (Local)
```bash
# Use the robust MCP server for LangFlow Desktop
# Command: /usr/bin/python3 /path/to/langflow_mcp_server_robust.py
python3 langflow_mcp_server_robust.py
```

**Expected Results:**
- ✅ 100% test success rate (11/11 scenarios)
- ⚡ Sub-15ms average response times  
- 🎯 Complete business intelligence across 7 categories

### Option B: AWS Cloud Deployment (Recommended)

#### 1. Deploy to AWS
```bash
# One-command deployment to AWS
cd aws-infrastructure
./deploy.sh
```

#### 2. Connect LangFlow to AWS
```bash
# Bridge automatically configured during deployment
# Use the generated command in LangFlow Desktop:
# /usr/bin/python3 /path/to/aws-mcp-bridge-configured.py
```

#### 3. Test Cloud Integration
```bash
# Test the AWS bridge
python3 test-aws-bridge.py
```

**AWS Benefits:**
- 🚀 **Serverless scaling** - Pay only for usage
- 🔒 **Enterprise security** - IAM, encryption, monitoring
- 🌍 **Global availability** - API Gateway worldwide
- 💰 **Cost efficient** - ~$20/month dev, ~$100/month prod

## AWS Architecture

### Infrastructure Components

The AWS deployment uses a modern serverless architecture for scalability and cost efficiency:

#### Core Services:
- **S3 Data Lake**: Object storage for Parquet files with intelligent tiering
- **Lambda Functions**: Serverless compute for DuckDB queries and MCP protocol
- **API Gateway**: RESTful HTTP endpoint with CORS and authentication
- **IAM Roles**: Secure service-to-service communication
- **CloudWatch**: Monitoring, logging, and alerting

#### Architecture Diagram:
```
LangFlow Desktop → STDIO Bridge → API Gateway → Lambda → DuckDB + S3
     ↓                ↓              ↓           ↓         ↓
  User Query    → JSON-RPC    → HTTP POST → Query Engine → Data Lake
```

### Data Flow:
1. **User Query** → LangFlow Desktop app
2. **STDIO Bridge** → Converts to HTTP API calls
3. **API Gateway** → Routes to appropriate Lambda function
4. **Lambda Functions** → Process MCP requests and execute DuckDB queries
5. **S3 Data Lake** → Serves Parquet files to DuckDB engine
6. **Response Path** → Results flow back through same chain

### Cost Optimization:
- **Pay-per-use** Lambda billing (no idle costs)
- **S3 Intelligent Tiering** for automatic cost optimization
- **API Gateway caching** for repeated queries
- **DuckDB efficiency** for fast analytical queries

### Security Features:
- **IAM Role-based Access** for all service communication
- **API Gateway throttling** to prevent abuse
- **CloudWatch monitoring** for security events
- **Encryption at rest and in transit**

### Deployment Files:
- `aws-infrastructure/main.tf` - Complete Terraform configuration
- `aws-infrastructure/deploy.sh` - One-command deployment script
- `aws-mcp-bridge.py` - STDIO to HTTP bridge for LangFlow
- `setup-aws-bridge.sh` - Automated bridge configuration

## Data Model

### DuckLake Dataset
The current implementation includes production-ready sample data stored as Parquet files in MinIO and accessible via DuckDB:

- **Cities** (10 rows): Major US cities with population, geographic regions, and demographic data
- **Sales** (1000 rows): E-commerce transactions across product categories, channels, and payment methods  
- **Customers** (200 rows): Customer profiles with segmentation, credit scores, and lifetime value analysis

### Business Intelligence Coverage
- **Geographic Analysis**: Population rankings, regional distribution, urban planning insights
- **Sales Analytics**: Revenue by category, channel effectiveness, discount impact analysis
- **Customer Intelligence**: Segmentation, lifetime value, credit risk correlation  
- **Financial Analytics**: Payment method preferences, transaction volume trends
- **Risk Analytics**: Credit score impact on customer value
- **Product Analytics**: Category performance, inventory optimization insights
- **Executive Dashboards**: High-level KPIs and performance monitoring

## Semantic Models

### Cities Cube
- **Dimensions**: city_name, state_name, region, state_abrv
- **Measures**: total_population, count, average_population
- **Use Cases**: Geographic analysis, market sizing, urban planning

### Sales Cube  
- **Dimensions**: product_category, channel, payment_method, discount_tier, date
- **Measures**: total_revenue, count, average_order_value, total_quantity, total_discount_amount
- **Use Cases**: Revenue optimization, channel analysis, pricing strategy

### Customers Cube
- **Dimensions**: customer_type, credit_score_tier, registration_date
- **Measures**: count, average_lifetime_value, total_lifetime_value, average_credit_score  
- **Use Cases**: Customer segmentation, risk assessment, value optimization

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
  "description": "What are the top 5 most populous cities?"
}
```

**Response:**
```json
{
  "natural_language": "What are the top 5 most populous cities?",
  "generated_query": {
    "measures": ["cities.total_population"],
    "dimensions": ["cities.city_name", "cities.state_name"], 
    "order": {"cities.total_population": "desc"},
    "limit": 5
  },
  "result": {
    "data": [
      {"cities.city_name": "New York", "cities.total_population": "8336817"},
      {"cities.city_name": "Los Angeles", "cities.total_population": "3979576"}
    ]
  }
}
```

### 2. get_schema_metadata
Get available cubes, dimensions, and measures.

### 3. suggest_analysis
Get analysis suggestions based on business questions.

## Usage Examples

### Connect to Cube.dev UI
- Open http://localhost:4000 for the Cube.dev playground
- View available cubes: cities, customers, sales
- Build queries interactively and test analytics

### Access MinIO Console (Optional)
- Open http://localhost:9001 for MinIO object storage console
- Login: admin / password123
- Browse Parquet files in semantic-lake bucket

### Query via Postgres Interface
```bash
psql -h localhost -p 15432 -U root
```

### Sample Queries

**Cities by Population:**
```json
{
  "measures": ["cities.total_population"],
  "dimensions": ["cities.city_name", "cities.region"],
  "order": {"cities.total_population": "desc"},
  "limit": 10
}
```

**Sales Performance by Category:**
```json
{
  "measures": ["sales.total_revenue", "sales.count"],
  "dimensions": ["sales.product_category"],
  "order": {"sales.total_revenue": "desc"}
}
```

**Customer Segmentation Analysis:**
```json
{
  "measures": ["customers.count", "customers.average_lifetime_value"],
  "dimensions": ["customers.customer_type", "customers.credit_score_tier"]
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

# Test with DuckLake query
curl -X POST http://localhost:4000/cubejs-api/v1/load \
  -H "Content-Type: application/json" \
  -d '{"query": {"measures": ["cities.total_population"], "dimensions": ["cities.city_name"], "limit": 3}}'

# Run comprehensive test suite
uv run python demo_test_suite.py
```

## Configuration

### Environment Variables
- `CUBEJS_API_SECRET`: API secret for Cube.dev authentication
- `CUBEJS_DEV_MODE`: Enable development mode (default: true)
- `CUBEJS_DB_DUCKDB_DATABASE_PATH`: DuckDB database path (default: ./lake_data/warehouse.db)
- `AWS_ACCESS_KEY_ID`: MinIO access key (default: admin)
- `AWS_SECRET_ACCESS_KEY`: MinIO secret key (default: password123)
- `AWS_ENDPOINT_URL`: MinIO endpoint (default: http://minio:9000)

### Custom Schema
Add new semantic models by creating YAML files in the `model/cubes/` directory following Cube.dev YAML conventions.

## Integration with AI Platforms

This MCP server enables agentic AI platforms to provide **conversational business intelligence** through natural language queries. The DuckLake semantic layer offers:

### For Business Users:
- **Natural Language Queries**: "What are our top performing sales channels?" 
- **Instant Business Insights**: Contextual analysis with KPIs and trends
- **Conversational Analytics**: Follow-up questions and data exploration

### For AI Platforms:
- **Plug-and-play Integration**: Standard MCP protocol, no custom database work
- **Business Semantics**: Queries use business terms (revenue, customers) not technical fields
- **Governed Data Access**: Consistent business logic and calculations across all queries
- **High Performance**: Sub-15ms response times for real-time conversational analytics

### LangFlow Desktop Integration

The semantic MCP server integrates seamlessly with LangFlow Desktop for conversational business intelligence. Choose your deployment option:

#### Option A: Local Development Integration
1. **Start the DuckLake stack**: `docker-compose -f docker-compose-lake.yml up -d`
2. **Configure LangFlow MCP Tools component**:
   - **Mode**: STDIO
   - **Command**: `/usr/bin/python3 /path/to/semantic_mcp/langflow_mcp_server_robust.py`
   - **Name**: semantic_mcp

#### Option B: AWS Cloud Integration (Recommended)
1. **Deploy to AWS**: `cd aws-infrastructure && ./deploy.sh`
2. **Configure LangFlow MCP Tools component**:
   - **Mode**: STDIO
   - **Command**: `/usr/bin/python3 /path/to/semantic_mcp/aws-mcp-bridge-configured.py`
   - **Name**: aws-semantic-mcp

#### LangFlow Process Flow:
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Chat Input    │───▶│   Chat Model     │───▶│   MCP Tools     │───▶│   Chat Output   │
│                 │    │   (OpenAI/etc)   │    │ semantic_mcp    │    │                 │
│ User Question   │    │                  │    │  or aws-mcp     │    │ Business Answer │
└─────────────────┘    └──────────────────┘    └─────────────────┘    └──────────────────┘
```

#### Example Queries in LangFlow:
- **"Show me revenue by product category"** → Real sales data analysis
- **"What are the top 5 cities by population?"** → Geographic insights
- **"How many customers do we have by type?"** → Customer segmentation
- **"What data is available?"** → Schema discovery

#### Chat Model System Prompt:
```
You are a business intelligence assistant with access to semantic data tools that can query business metrics about cities, sales, and customers.

When users ask business questions:
1. Use the query_semantic_layer tool for data queries
2. Use get_schema_metadata tool to understand available data
3. Provide clear, business-focused explanations of the results

Available data includes:
- Cities: population, names, states, regions
- Sales: revenue, categories, channels, payment methods
- Customers: counts, lifetime value, segments, credit scores
```

### Example Integration:
```python
# User: "Which customer types have the highest lifetime value?"
response = await mcp_client.call_tool(
    "query_semantic_layer",
    {"description": "Which customer types have the highest lifetime value?"}
)
# Result: "💎 Enterprise customers average $47K lifetime value (3.2x higher than Individual)"
```

## Troubleshooting

### Local Development Issues

1. **DuckLake Services Not Starting**
   ```bash
   docker-compose -f docker-compose-lake.yml down
   docker-compose -f docker-compose-lake.yml up -d --build
   ```

2. **Cube.js Connection Issues**
   ```bash
   docker-compose -f docker-compose-lake.yml logs cube
   ```

3. **MinIO/Parquet Access Issues**
   ```bash
   docker-compose -f docker-compose-lake.yml logs ducklake-setup
   ```

4. **Test Suite Failures**
   ```bash
   # Re-run setup and tests
   docker-compose -f docker-compose-lake.yml restart ducklake-setup
   uv run python demo_test_suite.py
   ```

5. **LangFlow Desktop MCP Issues**
   ```bash
   # Test the robust MCP server
   python3 langflow_mcp_server_robust.py
   # Check for port conflicts on 4000
   lsof -i :4000
   ```

### AWS Cloud Issues

1. **AWS Deployment Failures**
   ```bash
   # Check Terraform state
   cd aws-infrastructure
   terraform show
   
   # Retry deployment
   terraform apply
   ```

2. **API Gateway Connectivity**
   ```bash
   # Test API directly
   curl -X POST https://your-api-url/dev/mcp \
     -H "Content-Type: application/json" \
     -d '{"method": "initialize", "params": {}}'
   ```

3. **Bridge Configuration Issues**
   ```bash
   # Reconfigure bridge
   ./setup-aws-bridge.sh
   
   # Test bridge
   python3 test-aws-bridge.py
   ```

4. **Lambda Function Errors**
   ```bash
   # Check CloudWatch logs
   aws logs describe-log-groups --log-group-name-prefix /aws/lambda/
   ```

### LangFlow Integration Issues

1. **MCP Tools Not Working**
   - Verify STDIO mode is selected
   - Check Python path is correct
   - Ensure script has execute permissions

2. **"Query param is required" Errors**
   - Natural language processor issue
   - Try more specific business questions
   - Check robust MCP server fallback responses

3. **Desktop App Connectivity**
   - LangFlow Desktop may have sandbox restrictions
   - AWS cloud deployment recommended for stability

### Logs and Monitoring

```bash
# Local logs
docker-compose -f docker-compose-lake.yml logs

# AWS logs
aws logs tail /aws/lambda/semantic-mcp-server --follow

# Bridge debug mode
DEBUG=1 python3 aws-mcp-bridge-configured.py
```

### Performance Verification
Expected performance benchmarks:
- **Test Success Rate**: 100% (11/11 scenarios)
- **Average Response Time**: <15ms (local), <50ms (AWS)
- **Data Coverage**: 7 business intelligence categories
- **Natural Language Processing**: Automatic query generation from English