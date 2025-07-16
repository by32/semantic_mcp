# AWS Deployment for Semantic MCP

This directory contains the AWS infrastructure and deployment scripts for the Semantic MCP system.

## Architecture Overview

```
Internet → API Gateway → Lambda (MCP) → Lambda (DuckDB) → S3 Data Lake
```

### Components:
- **S3 Data Lake**: Stores Parquet files (cities, sales, customers)
- **DuckDB Lambda**: Executes analytical queries against S3 data
- **MCP Lambda**: Handles MCP protocol requests
- **API Gateway**: Provides REST API endpoint

## Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Terraform installed** (version 1.0+)
3. **Python 3.11** for building Lambda functions
4. **jq** for JSON processing (optional, for testing)

## Quick Start

### 1. Deploy Infrastructure

```bash
cd aws-infrastructure
./deploy.sh
```

This will:
- Create S3 bucket with encryption and versioning
- Deploy Lambda functions for DuckDB and MCP
- Set up API Gateway with proper routing
- Upload sample data to S3

### 2. Test the API

```bash
./test-api.sh
```

### 3. Update LangFlow

Use the new API Gateway endpoint in LangFlow:

```python
# Instead of local MCP server, use HTTP API
API_URL = "https://your-api-id.execute-api.us-east-1.amazonaws.com/dev/mcp"
```

## Manual Deployment Steps

### 1. Initialize Terraform

```bash
terraform init
```

### 2. Plan Deployment

```bash
terraform plan
```

### 3. Apply Infrastructure

```bash
terraform apply
```

### 4. Upload Data

```bash
./upload-data.sh
```

## Configuration

### Environment Variables

The system uses these environment variables:

- `S3_BUCKET`: S3 bucket name for data lake
- `DUCKDB_LAMBDA_ARN`: ARN of DuckDB Lambda function
- `AWS_REGION`: AWS region (default: us-east-1)

### Terraform Variables

```hcl
variable "aws_region" {
  default = "us-east-1"
}

variable "project_name" {
  default = "semantic-mcp"
}

variable "environment" {
  default = "dev"
}
```

## Cost Estimation

### Development Environment (~$20/month):
- S3 storage: ~$1 (1GB)
- Lambda executions: ~$5 (100K requests)
- API Gateway: ~$1 (100K requests)
- Data transfer: ~$3

### Production Environment (~$100/month):
- S3 storage: ~$10 (10GB + backups)
- Lambda executions: ~$50 (1M requests)
- API Gateway: ~$35 (1M requests)
- Data transfer: ~$15

## Monitoring

### CloudWatch Logs
- DuckDB Lambda: `/aws/lambda/semantic-mcp-duckdb-query`
- MCP Lambda: `/aws/lambda/semantic-mcp-mcp-server`

### CloudWatch Metrics
- Lambda duration, errors, throttles
- API Gateway request count, latency
- S3 request metrics

## Security

### IAM Roles
- Lambda execution role with S3 access
- Principle of least privilege

### S3 Security
- Bucket encryption enabled
- Public access blocked
- Versioning enabled

### API Gateway
- CORS enabled for web access
- Rate limiting can be added

## Troubleshooting

### Common Issues

1. **Lambda timeout**: Increase timeout in `main.tf`
2. **Memory issues**: Increase memory allocation
3. **S3 access denied**: Check IAM permissions
4. **Cold start latency**: Consider provisioned concurrency

### Debug Commands

```bash
# Check Lambda logs
aws logs tail /aws/lambda/semantic-mcp-duckdb-query --follow

# Test Lambda directly
aws lambda invoke \
  --function-name semantic-mcp-duckdb-query \
  --payload '{"query": "SELECT COUNT(*) FROM cities"}' \
  response.json

# Check S3 contents
aws s3 ls s3://semantic-mcp-datalake-dev --recursive
```

## Scaling

### Auto Scaling
- Lambda automatically scales based on demand
- API Gateway handles high concurrency
- S3 scales infinitely

### Performance Optimization
- DuckDB optimized for analytical queries
- S3 intelligent tiering for cost optimization
- CloudFront can be added for global distribution

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

⚠️ **Warning**: This will delete all data in S3 and cannot be undone.

## Next Steps

1. **Monitor costs** in AWS Cost Explorer
2. **Set up alerts** for unusual activity
3. **Add authentication** for production use
4. **Implement CI/CD** for automated deployments
5. **Add more data sources** to the data lake

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review Terraform state
3. Test individual components
4. Check AWS service quotas