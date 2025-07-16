#!/bin/bash
# Build DuckDB Query Lambda Function

set -e

echo "Building DuckDB Query Lambda Function..."

# Create function directory
mkdir -p duckdb-function

# Create Lambda function
cat > duckdb-function/lambda_function.py << 'EOF'
import json
import os
import boto3
import duckdb
from typing import Dict, Any

def lambda_handler(event, context):
    """
    DuckDB Query Lambda Function
    Executes queries against S3 data lake using DuckDB
    """
    try:
        # Get query from event
        query = event.get('query', '')
        if not query:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Query parameter is required'})
            }
        
        # Initialize DuckDB connection
        conn = duckdb.connect()
        
        # Install and load S3 extension
        conn.execute("INSTALL httpfs")
        conn.execute("LOAD httpfs")
        
        # Configure S3 access using Lambda's IAM role
        s3_bucket = os.environ['S3_BUCKET']
        
        # Create views for S3 data
        conn.execute(f"""
            CREATE OR REPLACE VIEW cities AS 
            SELECT * FROM read_parquet('s3://{s3_bucket}/cities/*.parquet')
        """)
        
        conn.execute(f"""
            CREATE OR REPLACE VIEW sales AS 
            SELECT * FROM read_parquet('s3://{s3_bucket}/sales/*.parquet')
        """)
        
        conn.execute(f"""
            CREATE OR REPLACE VIEW customers AS 
            SELECT * FROM read_parquet('s3://{s3_bucket}/customers/*.parquet')
        """)
        
        # Execute query
        result = conn.execute(query).fetchdf()
        
        # Convert to JSON-serializable format
        result_dict = result.to_dict('records')
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': result_dict,
                'row_count': len(result_dict)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    finally:
        if 'conn' in locals():
            conn.close()
EOF

# Create deployment package
cd duckdb-function
zip -r ../duckdb-query.zip .
cd ..

# Cleanup
rm -rf duckdb-function

echo "DuckDB function built successfully: duckdb-query.zip"