#!/bin/bash
# Upload data to S3 bucket

set -e

echo "📦 Uploading data to S3..."

# Get bucket name from Terraform output
BUCKET_NAME=$(terraform output -raw s3_bucket_name)

if [ -z "$BUCKET_NAME" ]; then
    echo "❌ Could not get S3 bucket name from Terraform"
    exit 1
fi

echo "Using bucket: $BUCKET_NAME"

# Check if data directory exists
if [ ! -d "../data" ]; then
    echo "❌ Data directory not found. Creating sample data..."
    mkdir -p ../data
    
    # Create sample data script
    cat > ../data/create_sample_data.py << 'EOF'
import pandas as pd
import os

# Create sample cities data
cities_data = [
    {"city_name": "New York", "population": 8336817, "state": "NY"},
    {"city_name": "Los Angeles", "population": 3979576, "state": "CA"},
    {"city_name": "Chicago", "population": 2693976, "state": "IL"},
    {"city_name": "Houston", "population": 2320268, "state": "TX"},
    {"city_name": "Phoenix", "population": 1680992, "state": "AZ"}
]

# Create sample sales data
sales_data = [
    {"product_category": "Home & Garden", "order_value": 150.25, "quantity": 2},
    {"product_category": "Sports", "order_value": 89.99, "quantity": 1},
    {"product_category": "Clothing", "order_value": 65.50, "quantity": 3},
    {"product_category": "Electronics", "order_value": 299.99, "quantity": 1},
    {"product_category": "Books", "order_value": 25.99, "quantity": 2}
]

# Create sample customers data
customers_data = [
    {"customer_name": "John Doe", "customer_type": "Premium", "city": "New York"},
    {"customer_name": "Jane Smith", "customer_type": "Standard", "city": "Los Angeles"},
    {"customer_name": "Bob Johnson", "customer_type": "Premium", "city": "Chicago"}
]

# Save as Parquet files
pd.DataFrame(cities_data).to_parquet("cities.parquet", index=False)
pd.DataFrame(sales_data).to_parquet("sales.parquet", index=False)
pd.DataFrame(customers_data).to_parquet("customers.parquet", index=False)

print("Sample data created successfully!")
EOF

    # Run the script
    cd ../data
    python3 create_sample_data.py
    cd ../aws-infrastructure
fi

# Upload data files
echo "Uploading cities data..."
aws s3 cp ../data/cities.parquet s3://$BUCKET_NAME/cities/cities.parquet

echo "Uploading sales data..."
aws s3 cp ../data/sales.parquet s3://$BUCKET_NAME/sales/sales.parquet

echo "Uploading customers data..."
aws s3 cp ../data/customers.parquet s3://$BUCKET_NAME/customers/customers.parquet

# Verify uploads
echo "Verifying uploads..."
aws s3 ls s3://$BUCKET_NAME --recursive

echo "✅ Data upload complete!"