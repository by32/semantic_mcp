#!/bin/bash
# Build DuckDB Lambda Layer

set -e

echo "Building DuckDB Lambda Layer..."

# Create layer directory
mkdir -p layer/python

# Create virtual environment
python3 -m venv layer-venv
source layer-venv/bin/activate

# Install dependencies
pip install duckdb boto3 pandas pyarrow

# Copy packages to layer
cp -r layer-venv/lib/python3.11/site-packages/* layer/python/

# Create layer zip
cd layer
zip -r ../duckdb-layer.zip python/
cd ..

# Cleanup
rm -rf layer layer-venv

echo "DuckDB layer built successfully: duckdb-layer.zip"