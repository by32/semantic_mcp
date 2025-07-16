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

# Setup the bridge automatically
echo "🌉 Setting up LangFlow bridge..."
cd ..
./setup-aws-bridge.sh

echo ""
echo "🎉 Complete setup finished!"
echo ""
echo "📋 LangFlow Configuration:"
echo "   Mode: STDIO"
echo "   Command: /usr/bin/python3 $(pwd)/aws-mcp-bridge-configured.py"
echo "   Name: aws-semantic-mcp"
echo ""
echo "Next steps:"
echo "1. Update LangFlow Desktop with the new command above"
echo "2. Test your queries - they now run on AWS!"
echo "3. Monitor costs in AWS Cost Explorer"
echo "4. Check CloudWatch logs for any issues"