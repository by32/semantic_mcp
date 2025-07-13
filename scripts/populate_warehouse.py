#!/usr/bin/env python3
"""
Populate DuckDB warehouse with data directly
"""

import os
import duckdb
import pandas as pd
from datetime import datetime, timedelta
import random

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
    
    for i in range(1, 501):  # 500 sales records
        city_id = random.randint(1, 10)
        date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 180))  # Last 6 months
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
    
    for i in range(1, 101):  # 100 customers
        city_id = random.randint(1, 10)
        customer_type = random.choice(customer_types)
        registration_date = datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
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

def populate_warehouse():
    """Populate DuckDB warehouse with data"""
    print("Populating DuckDB warehouse...")
    
    # Connect to warehouse
    conn = duckdb.connect('/lake_data/warehouse.db')
    
    # Create datasets
    datasets = create_sample_data()
    
    # Insert data into tables
    for table_name, df in datasets.items():
        print(f"Inserting {len(df)} rows into {table_name}")
        
        # Clear existing data
        conn.execute(f"DELETE FROM {table_name}")
        
        # Insert new data
        conn.register(f'{table_name}_df', df)
        conn.execute(f"INSERT INTO {table_name} SELECT * FROM {table_name}_df")
        
        # Verify
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"✅ {table_name}: {count} rows")
    
    conn.close()
    print("🎉 Warehouse populated successfully!")

if __name__ == "__main__":
    populate_warehouse()