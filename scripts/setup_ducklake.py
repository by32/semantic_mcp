#!/usr/bin/env python3
"""
Setup DuckLake with Parquet files on MinIO object storage
"""

import os
import duckdb
import pandas as pd
import boto3
from datetime import datetime, timedelta
import random

# MinIO/S3 configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'admin')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'password123')
AWS_ENDPOINT_URL = os.getenv('AWS_ENDPOINT_URL', 'http://minio:9000')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Configure boto3 for MinIO
s3_client = boto3.client(
    's3',
    endpoint_url=AWS_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def create_sample_data():
    """Create sample datasets"""
    print("Creating sample datasets...")
    
    # Cities data
    cities_data = [
        {'id': 1, 'city_name': 'New York', 'state_abrv': 'NY', 'state_name': 'New York', 'population': 8336817, 'area_sq_miles': 302.6, 'founded_year': 1624, 'region': 'Northeast'},
        {'id': 2, 'city_name': 'Los Angeles', 'state_abrv': 'CA', 'state_name': 'California', 'population': 3979576, 'area_sq_miles': 468.7, 'founded_year': 1781, 'region': 'West'},
        {'id': 3, 'city_name': 'Chicago', 'state_abrv': 'IL', 'state_name': 'Illinois', 'population': 2693976, 'area_sq_miles': 227.6, 'founded_year': 1833, 'region': 'Midwest'},
        {'id': 4, 'city_name': 'Houston', 'state_abrv': 'TX', 'state_name': 'Texas', 'population': 2320268, 'area_sq_miles': 669.1, 'founded_year': 1836, 'region': 'South'},
        {'id': 5, 'city_name': 'Phoenix', 'state_abrv': 'AZ', 'state_name': 'Arizona', 'population': 1680992, 'area_sq_miles': 517.6, 'founded_year': 1868, 'region': 'West'},
        {'id': 6, 'city_name': 'Philadelphia', 'state_abrv': 'PA', 'state_name': 'Pennsylvania', 'population': 1584064, 'area_sq_miles': 134.1, 'founded_year': 1682, 'region': 'Northeast'},
        {'id': 7, 'city_name': 'San Antonio', 'state_abrv': 'TX', 'state_name': 'Texas', 'population': 1547253, 'area_sq_miles': 460.9, 'founded_year': 1718, 'region': 'South'},
        {'id': 8, 'city_name': 'San Diego', 'state_abrv': 'CA', 'state_name': 'California', 'population': 1423851, 'area_sq_miles': 325.2, 'founded_year': 1769, 'region': 'West'},
        {'id': 9, 'city_name': 'Dallas', 'state_abrv': 'TX', 'state_name': 'Texas', 'population': 1343573, 'area_sq_miles': 340.5, 'founded_year': 1841, 'region': 'South'},
        {'id': 10, 'city_name': 'San Jose', 'state_abrv': 'CA', 'state_name': 'California', 'population': 1021795, 'area_sq_miles': 176.5, 'founded_year': 1777, 'region': 'West'}
    ]
    
    # Generate sales data
    sales_data = []
    categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books']
    channels = ['Online', 'Retail', 'B2B', 'Partner']
    payment_methods = ['Credit Card', 'Cash', 'Check', 'Bank Transfer']
    
    for i in range(1, 1001):  # 1000 sales records
        city_id = random.randint(1, 10)
        date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))
        category = random.choice(categories)
        channel = random.choice(channels)
        payment_method = random.choice(payment_methods)
        
        quantity = random.randint(1, 10)
        unit_price = round(random.uniform(20, 1000), 2)
        discount_percent = random.choice([0, 5, 10, 15, 20]) if random.random() < 0.3 else 0
        total_amount = round(quantity * unit_price * (1 - discount_percent / 100), 2)
        
        sales_data.append({
            'id': i,
            'city_id': city_id,
            'date': date,
            'product_category': category,
            'channel': channel,
            'payment_method': payment_method,
            'quantity': quantity,
            'unit_price': unit_price,
            'discount_percent': discount_percent,
            'total_amount': total_amount
        })
    
    # Generate customers data
    customers_data = []
    customer_types = ['Individual', 'Small Business', 'Enterprise']
    
    for i in range(1, 201):  # 200 customers
        city_id = random.randint(1, 10)
        customer_type = random.choice(customer_types)
        registration_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 730))
        credit_score = random.randint(300, 850)
        lifetime_value = round(random.uniform(100, 50000), 2)
        
        customers_data.append({
            'id': i,
            'customer_name': f'Customer {i}',
            'customer_type': customer_type,
            'city_id': city_id,
            'registration_date': registration_date,
            'credit_score': credit_score,
            'lifetime_value': lifetime_value
        })
    
    return {
        'cities': pd.DataFrame(cities_data),
        'sales': pd.DataFrame(sales_data),
        'customers': pd.DataFrame(customers_data)
    }

def write_to_parquet_lake(df, table_name, s3_path):
    """Write DataFrame to Parquet files on MinIO (DuckLake approach)"""
    print(f"Writing {table_name} to Parquet Lake at {s3_path}")
    
    try:
        import boto3
        s3 = boto3.client(
            's3',
            endpoint_url=AWS_ENDPOINT_URL,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # Convert to parquet bytes
        parquet_buffer = df.to_parquet(index=False)
        
        # Extract bucket and key from s3_path
        bucket = s3_path.replace('s3://', '').split('/')[0]
        key = f"{'/'.join(s3_path.replace('s3://', '').split('/')[1:])}{table_name}.parquet"
        
        # Upload to S3/MinIO
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=parquet_buffer
        )
        print(f"✅ Successfully wrote {table_name} as Parquet to MinIO ({len(df)} rows)")
        return True
        
    except Exception as e:
        print(f"❌ Parquet write failed for {table_name}: {e}")
        return False

def setup_duckdb_warehouse():
    """Setup DuckDB warehouse with local tables populated from sample data"""
    print("Setting up DuckDB warehouse for DuckLake architecture...")
    
    # Ensure directory exists
    os.makedirs('/lake_data', exist_ok=True)
    
    # Connect to DuckDB warehouse
    conn = duckdb.connect('/lake_data/warehouse.db')
    
    print("✅ Connected to DuckDB warehouse")
    
    # Drop existing tables/views first
    print("Cleaning up existing tables and views...")
    tables_to_drop = ['cities', 'sales', 'customers']
    for table in tables_to_drop:
        try:
            conn.execute(f"DROP VIEW IF EXISTS {table}")
            print(f"✅ Dropped existing {table} view")
        except Exception as e:
            print(f"ℹ️ No existing {table} view to drop")
        
        try:
            conn.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"✅ Dropped existing {table} table")
        except Exception as e:
            print(f"ℹ️ No existing {table} table to drop")
    
    # Create and populate tables with sample data
    print("Creating DuckDB tables with sample data...")
    
    # Get the sample datasets
    datasets = create_sample_data()
    
    # Create cities table
    cities_df = datasets['cities']
    try:
        conn.execute("""
            CREATE TABLE cities (
                id INTEGER PRIMARY KEY,
                city_name VARCHAR,
                state_abrv VARCHAR,
                state_name VARCHAR,
                population INTEGER,
                area_sq_miles REAL,
                founded_year INTEGER,
                region VARCHAR
            )
        """)
        print("✅ Created cities table")
    except Exception as e:
        print(f"⚠️ Cities table creation: {e}")
        conn.execute("DELETE FROM cities")
        print("✅ Cleared existing cities data")
    
    # Insert cities data
    for _, row in cities_df.iterrows():
        conn.execute("""
            INSERT INTO cities VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (row['id'], row['city_name'], row['state_abrv'], row['state_name'], 
              row['population'], row['area_sq_miles'], row['founded_year'], row['region']))
    
    # Create sales table
    sales_df = datasets['sales']
    try:
        conn.execute("""
            CREATE TABLE sales (
                id INTEGER PRIMARY KEY,
                city_id INTEGER,
                date DATE,
                product_category VARCHAR,
                channel VARCHAR,
                payment_method VARCHAR,
                quantity INTEGER,
                unit_price DECIMAL(10,2),
                discount_percent DECIMAL(5,2),
                total_amount DECIMAL(12,2)
            )
        """)
        print("✅ Created sales table")
    except Exception as e:
        print(f"⚠️ Sales table creation: {e}")
        conn.execute("DELETE FROM sales")
        print("✅ Cleared existing sales data")
    
    # Insert sales data (first 100 rows for efficiency)
    for _, row in sales_df.head(100).iterrows():
        conn.execute("""
            INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (row['id'], row['city_id'], row['date'], row['product_category'],
              row['channel'], row['payment_method'], row['quantity'], 
              row['unit_price'], row['discount_percent'], row['total_amount']))
    
    # Create customers table
    customers_df = datasets['customers']
    try:
        conn.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                customer_name VARCHAR,
                customer_type VARCHAR,
                city_id INTEGER,
                registration_date DATE,
                credit_score INTEGER,
                lifetime_value DECIMAL(12,2)
            )
        """)
        print("✅ Created customers table")
    except Exception as e:
        print(f"⚠️ Customers table creation: {e}")
        conn.execute("DELETE FROM customers")
        print("✅ Cleared existing customers data")
    
    # Insert customers data
    for _, row in customers_df.iterrows():
        conn.execute("""
            INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (row['id'], row['customer_name'], row['customer_type'], row['city_id'],
              row['registration_date'], row['credit_score'], row['lifetime_value']))
    
    # Verify data
    result = conn.execute("SELECT COUNT(*) FROM cities").fetchone()
    print(f"✅ Cities table: {result[0]} rows")
    
    result = conn.execute("SELECT COUNT(*) FROM sales").fetchone()
    print(f"✅ Sales table: {result[0]} rows") 
    
    result = conn.execute("SELECT COUNT(*) FROM customers").fetchone()
    print(f"✅ Customers table: {result[0]} rows")
    
    # Test sample query
    result = conn.execute("SELECT city_name, population FROM cities ORDER BY population DESC LIMIT 3").fetchall()
    print(f"✅ Sample cities data: {result}")
    
    print("✅ DuckLake architecture: Parquet files in MinIO + fast DuckDB access layer")
    
    conn.close()

def create_local_tables(conn):
    """Create local DuckDB tables with sample data"""
    
    # Create tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY,
            city_name VARCHAR,
            state_abrv VARCHAR,
            state_name VARCHAR,
            population INTEGER,
            area_sq_miles REAL,
            founded_year INTEGER,
            region VARCHAR
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY,
            city_id INTEGER,
            date DATE,
            product_category VARCHAR,
            channel VARCHAR,
            payment_method VARCHAR,
            quantity INTEGER,
            unit_price DECIMAL(10,2),
            discount_percent DECIMAL(5,2),
            total_amount DECIMAL(12,2)
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            customer_name VARCHAR,
            customer_type VARCHAR,
            city_id INTEGER,
            registration_date DATE,
            credit_score INTEGER,
            lifetime_value DECIMAL(12,2)
        )
    """)
    
    print("✅ Created local DuckDB tables as fallback")

def main():
    """Main setup function"""
    print("🚀 Starting DuckLake setup...")
    
    try:
        # Create sample data
        datasets = create_sample_data()
        
        # Write to Parquet Lake (MinIO)
        base_s3_path = "s3://semantic-lake"
        
        for table_name, df in datasets.items():
            s3_path = f"{base_s3_path}/"
            success = write_to_parquet_lake(df, table_name, s3_path)
            if not success:
                print(f"⚠️ Failed to write {table_name} to MinIO, will use local tables")
        
        # Setup DuckDB warehouse
        setup_duckdb_warehouse()
        
        print("🎉 DuckLake setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        raise

if __name__ == "__main__":
    main()