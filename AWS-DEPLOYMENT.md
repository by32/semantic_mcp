# AWS Deployment Guide

## Overview

This guide covers deploying the Semantic MCP Server to AWS for production use with LangFlow Desktop. The AWS deployment provides a scalable, serverless architecture that's more stable than local Docker containers.

## Prerequisites

### AWS Account Setup
1. **AWS CLI configured** with appropriate credentials
2. **Terraform installed** (version 1.0+)
3. **AWS permissions** for:
   - S3 bucket creation and management
   - Lambda function deployment
   - API Gateway configuration
   - IAM role creation
   - CloudWatch logs access

### Required Tools
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Install Terraform
brew install terraform  # macOS
# or
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip

# Configure AWS credentials
aws configure
```

## Deployment Process

### Step 1: One-Command Deployment
```bash
# Deploy everything to AWS
cd aws-infrastructure
./deploy.sh
```

This script will:
- Initialize Terraform
- Create S3 data lake with sample data
- Deploy Lambda functions for DuckDB and MCP
- Set up API Gateway with proper CORS
- Configure IAM roles and permissions
- Upload Parquet data files to S3
- Set up the LangFlow bridge automatically

### Step 2: Verify Deployment
```bash
# Test the deployment
cd ..
python3 test-aws-bridge.py
```

Expected output:
```
🧪 Testing AWS MCP Bridge
==============================
1. Testing initialize...
   ✅ Initialize successful
   📡 Connected to: AWS Semantic MCP Server

2. Testing tools/list...
   ✅ Found 3 tools
      - query_semantic_layer
      - get_schema_metadata
      - suggest_analysis

3. Testing query_semantic_layer...
   ✅ Query successful
   📊 Got 5 rows of data

🎉 AWS Bridge test successful!
✅ Ready for LangFlow integration
```

## Architecture Components

### Lambda Functions

#### 1. DuckDB Query Engine (`duckdb-lambda`)
- **Purpose**: Execute analytical queries against S3 data lake
- **Runtime**: Python 3.11 with DuckDB layer
- **Memory**: 512MB - 3GB (auto-scaling)
- **Timeout**: 30 seconds
- **Triggers**: API Gateway POST requests

#### 2. MCP Protocol Handler (`mcp-lambda`)
- **Purpose**: Handle Model Context Protocol requests
- **Runtime**: Python 3.11
- **Memory**: 256MB
- **Timeout**: 30 seconds
- **Integration**: Calls DuckDB Lambda for data queries

### S3 Data Lake

#### Bucket Structure:
```
semantic-mcp-data-lake-{random-suffix}/
├── data/
│   ├── cities.parquet
│   ├── sales.parquet
│   └── customers.parquet
├── schema/
│   └── cube-configs/
└── logs/
    └── query-logs/
```

#### Features:
- **Intelligent Tiering**: Automatic cost optimization
- **Versioning**: Enabled for data recovery
- **Encryption**: AES-256 server-side encryption
- **Access Logging**: CloudTrail integration

### API Gateway

#### Endpoints:
- `POST /dev/mcp` - Main MCP protocol endpoint
- `GET /dev/health` - Health check endpoint
- `OPTIONS /*` - CORS preflight handling

#### Features:
- **CORS enabled** for web applications
- **Request validation** with JSON schema
- **Rate limiting** to prevent abuse
- **CloudWatch integration** for monitoring

## LangFlow Integration

### Configuration
After deployment, use these settings in LangFlow Desktop:

**MCP Tools Component:**
- **Mode**: STDIO
- **Command**: `/usr/bin/python3 /path/to/aws-mcp-bridge-configured.py`
- **Name**: `aws-semantic-mcp`

### Bridge Architecture
```
LangFlow Desktop (STDIO) → Bridge (HTTP) → API Gateway → Lambda → S3
```

The bridge (`aws-mcp-bridge.py`) handles:
- **Protocol conversion** from STDIO to HTTP
- **Session management** for request tracking
- **Error handling** with fallback responses
- **Debug logging** for troubleshooting

## Monitoring and Logging

### CloudWatch Logs
```bash
# View MCP server logs
aws logs tail /aws/lambda/semantic-mcp-server --follow

# View DuckDB query logs
aws logs tail /aws/lambda/duckdb-query-engine --follow

# View API Gateway logs
aws logs tail /aws/apigateway/semantic-mcp-api --follow
```

### CloudWatch Metrics
- **Lambda invocations** and duration
- **API Gateway request count** and latency
- **S3 request metrics** and costs
- **Error rates** and failure patterns

### Cost Monitoring
```bash
# Check current month costs
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

## Security Configuration

### IAM Roles

#### Lambda Execution Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::semantic-mcp-data-lake-*",
        "arn:aws:s3:::semantic-mcp-data-lake-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

#### API Gateway Execution Role
- **CloudWatch Logs**: Write access for request logging
- **Lambda Invoke**: Execute Lambda functions
- **X-Ray Tracing**: Optional performance monitoring

### Network Security
- **VPC**: Optional for enhanced security
- **Security Groups**: Restrict Lambda network access
- **API Gateway**: IP whitelisting if needed

## Performance Optimization

### Lambda Optimization
```python
# Provisioned concurrency for consistent performance
resource "aws_lambda_provisioned_concurrency_config" "mcp_server" {
  function_name                     = aws_lambda_function.mcp_server.function_name
  provisioned_concurrent_executions = 2
  qualifier                        = "$LATEST"
}
```

### S3 Optimization
- **Intelligent Tiering**: Automatic cost optimization
- **Multipart uploads**: For large data files
- **CloudFront CDN**: For global data distribution

### DuckDB Optimization
- **Connection pooling**: Reuse connections across invocations
- **Query caching**: Cache frequent query results
- **Parallel processing**: Leverage DuckDB's multi-threading

## Troubleshooting

### Common Issues

#### 1. Deployment Failures
```bash
# Check Terraform state
terraform show

# Force refresh
terraform refresh

# Destroy and recreate
terraform destroy
terraform apply
```

#### 2. Lambda Timeout Issues
```bash
# Increase timeout in main.tf
resource "aws_lambda_function" "mcp_server" {
  timeout = 60  # Increase from 30
}
```

#### 3. S3 Access Denied
```bash
# Check bucket policy
aws s3api get-bucket-policy --bucket semantic-mcp-data-lake-xyz

# Test access
aws s3 ls s3://semantic-mcp-data-lake-xyz/data/
```

#### 4. API Gateway CORS Issues
```bash
# Test CORS preflight
curl -X OPTIONS https://your-api-url/dev/mcp \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type"
```

### Debug Mode
```bash
# Enable debug logging
DEBUG=1 python3 aws-mcp-bridge-configured.py

# Check bridge logs
tail -f /tmp/aws-mcp-bridge.log
```

## Cost Estimation

### Development Environment (~$20/month)
- **Lambda**: ~$5 (1M requests, 1GB-second)
- **S3**: ~$3 (100GB storage, 1K requests)
- **API Gateway**: ~$10 (1M requests)
- **Data Transfer**: ~$2 (10GB outbound)

### Production Environment (~$100/month)
- **Lambda**: ~$25 (10M requests, 10GB-second)
- **S3**: ~$15 (1TB storage, 100K requests)
- **API Gateway**: ~$35 (10M requests)
- **Data Transfer**: ~$25 (100GB outbound)

## Maintenance

### Regular Tasks
1. **Monitor costs** weekly via AWS Cost Explorer
2. **Review CloudWatch logs** for errors
3. **Update Lambda functions** with new data
4. **Backup S3 data** regularly
5. **Update security policies** as needed

### Scaling Considerations
- **Lambda concurrency limits**: Default 1000 concurrent executions
- **API Gateway limits**: 10,000 requests per second
- **S3 throughput**: 3,500 PUT/POST, 5,500 GET per prefix per second
- **DuckDB performance**: Scales with Lambda memory allocation

## Cleanup

### Destroy Infrastructure
```bash
# Remove all AWS resources
cd aws-infrastructure
terraform destroy
```

### Manual Cleanup
```bash
# Remove any remaining S3 objects
aws s3 rm s3://semantic-mcp-data-lake-xyz --recursive

# Check for orphaned resources
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Project,Values=semantic-mcp
```

## Next Steps

1. **Scale data lake** with more diverse datasets
2. **Add authentication** for production use
3. **Implement caching** for better performance
4. **Add monitoring dashboards** in CloudWatch
5. **Set up CI/CD pipeline** for automated deployments