#!/bin/bash
# Deploy Semantic MCP to AWS

set -e

echo "🚀 Deploying Semantic MCP to AWS..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI not configured. Please run 'aws configure'"
    exit 1
fi

# Make build scripts executable
chmod +x build-duckdb-layer.sh
chmod +x build-duckdb-function.sh
chmod +x build-mcp-function.sh

# Initialize Terraform
echo "📋 Initializing Terraform..."
terraform init

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -out=tfplan

# Apply deployment
echo "🚀 Deploying infrastructure..."
terraform apply tfplan

# Get outputs
echo "📊 Deployment complete!"
echo "S3 Bucket: $(terraform output -raw s3_bucket_name)"
echo "API Gateway URL: $(terraform output -raw api_gateway_url)"
echo "DuckDB Lambda ARN: $(terraform output -raw duckdb_lambda_arn)"

# Upload data
echo "📦 Uploading data to S3..."
./upload-data.sh

echo "✅ Deployment successful!"
echo ""
echo "Next steps:"
echo "1. Test the API Gateway endpoint"
echo "2. Update LangFlow to use the new API"
echo "3. Monitor CloudWatch logs for any issues"