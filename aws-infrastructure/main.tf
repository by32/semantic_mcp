# Semantic MCP AWS Infrastructure
# Phase 1: S3 Data Lake + Basic Services

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "semantic-mcp"
}

variable "environment" {
  description = "Environment (dev/staging/prod)"
  type        = string
  default     = "dev"
}

# S3 Bucket for Data Lake
resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-datalake-${var.environment}"
  
  tags = {
    Name        = "${var.project_name}-datalake"
    Environment = var.environment
    Project     = var.project_name
  }
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "data_lake_versioning" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake_encryption" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "data_lake_pab" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 Bucket Intelligent Tiering (cost optimization)
resource "aws_s3_bucket_intelligent_tiering_configuration" "data_lake_tiering" {
  bucket = aws_s3_bucket.data_lake.id
  name   = "EntireBucket"

  status = "Enabled"
}

# IAM Role for Lambda Functions
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for Lambda to access S3
resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "${var.project_name}-lambda-s3-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.data_lake.arn,
          "${aws_s3_bucket.data_lake.arn}/*"
        ]
      }
    ]
  })
}

# Attach basic Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# DuckDB Lambda Layer (for DuckDB dependencies)
resource "aws_lambda_layer_version" "duckdb_layer" {
  filename      = "duckdb-layer.zip"
  layer_name    = "${var.project_name}-duckdb-layer"
  description   = "DuckDB and dependencies for query execution"
  
  compatible_runtimes = ["python3.11"]
  
  depends_on = [null_resource.build_duckdb_layer]
}

# Build DuckDB layer
resource "null_resource" "build_duckdb_layer" {
  provisioner "local-exec" {
    command = "./build-duckdb-layer.sh"
  }
  
  triggers = {
    always_run = timestamp()
  }
}

# DuckDB Query Lambda Function
resource "aws_lambda_function" "duckdb_query" {
  filename      = "duckdb-query.zip"
  function_name = "${var.project_name}-duckdb-query"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  timeout       = 900  # 15 minutes
  memory_size   = 3008  # Maximum memory

  layers = [aws_lambda_layer_version.duckdb_layer.arn]

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.data_lake.bucket
      AWS_REGION = var.aws_region
    }
  }

  depends_on = [null_resource.build_duckdb_function]
}

# Build DuckDB function
resource "null_resource" "build_duckdb_function" {
  provisioner "local-exec" {
    command = "./build-duckdb-function.sh"
  }
  
  triggers = {
    always_run = timestamp()
  }
}

# API Gateway for MCP Server
resource "aws_api_gateway_rest_api" "mcp_api" {
  name        = "${var.project_name}-mcp-api"
  description = "MCP Server API Gateway"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# API Gateway Resource
resource "aws_api_gateway_resource" "mcp_resource" {
  rest_api_id = aws_api_gateway_rest_api.mcp_api.id
  parent_id   = aws_api_gateway_rest_api.mcp_api.root_resource_id
  path_part   = "mcp"
}

# API Gateway Method
resource "aws_api_gateway_method" "mcp_method" {
  rest_api_id   = aws_api_gateway_rest_api.mcp_api.id
  resource_id   = aws_api_gateway_resource.mcp_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# API Gateway Integration
resource "aws_api_gateway_integration" "mcp_integration" {
  rest_api_id = aws_api_gateway_rest_api.mcp_api.id
  resource_id = aws_api_gateway_resource.mcp_resource.id
  http_method = aws_api_gateway_method.mcp_method.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.mcp_server.invoke_arn
}

# MCP Server Lambda Function
resource "aws_lambda_function" "mcp_server" {
  filename      = "mcp-server.zip"
  function_name = "${var.project_name}-mcp-server"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.11"
  timeout       = 120
  memory_size   = 1024

  environment {
    variables = {
      S3_BUCKET = aws_s3_bucket.data_lake.bucket
      DUCKDB_LAMBDA_ARN = aws_lambda_function.duckdb_query.arn
      AWS_REGION = var.aws_region
    }
  }

  depends_on = [null_resource.build_mcp_function]
}

# Build MCP function
resource "null_resource" "build_mcp_function" {
  provisioner "local-exec" {
    command = "./build-mcp-function.sh"
  }
  
  triggers = {
    always_run = timestamp()
  }
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.mcp_server.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.mcp_api.execution_arn}/*/*"
}

# API Gateway Deployment
resource "aws_api_gateway_deployment" "mcp_deployment" {
  depends_on = [
    aws_api_gateway_integration.mcp_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.mcp_api.id
  stage_name  = var.environment
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.project_name}"
  retention_in_days = 14
}

# Outputs
output "s3_bucket_name" {
  description = "Name of the S3 data lake bucket"
  value       = aws_s3_bucket.data_lake.bucket
}

output "api_gateway_url" {
  description = "API Gateway URL for MCP server"
  value       = "${aws_api_gateway_rest_api.mcp_api.execution_arn}/${var.environment}/mcp"
}

output "duckdb_lambda_arn" {
  description = "DuckDB Lambda function ARN"
  value       = aws_lambda_function.duckdb_query.arn
}