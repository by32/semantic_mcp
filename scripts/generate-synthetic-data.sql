-- Complex synthetic dataset with multiple business entities and relationships

-- Companies table
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    company_name VARCHAR,
    industry VARCHAR,
    founded_year INTEGER,
    headquarters_city_id INTEGER,
    revenue_category VARCHAR, -- Small, Medium, Large, Enterprise
    employee_count INTEGER,
    FOREIGN KEY (headquarters_city_id) REFERENCES cities(id)
);

-- Products table
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    product_name VARCHAR,
    category VARCHAR,
    subcategory VARCHAR,
    brand VARCHAR,
    unit_cost DECIMAL(10,2),
    unit_price DECIMAL(10,2),
    launch_date DATE,
    discontinue_date DATE
);

-- Customers table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    customer_name VARCHAR,
    customer_type VARCHAR, -- Individual, Small Business, Enterprise
    city_id INTEGER,
    registration_date DATE,
    credit_score INTEGER,
    lifetime_value DECIMAL(12,2),
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

-- Sales representatives table
CREATE TABLE sales_reps (
    id INTEGER PRIMARY KEY,
    rep_name VARCHAR,
    hire_date DATE,
    territory_region VARCHAR,
    performance_tier VARCHAR, -- Junior, Senior, Expert, Director
    annual_quota DECIMAL(12,2)
);

-- Detailed transactions table
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    transaction_date DATE,
    customer_id INTEGER,
    sales_rep_id INTEGER,
    product_id INTEGER,
    city_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount_percent DECIMAL(5,2),
    total_amount DECIMAL(12,2),
    payment_method VARCHAR,
    channel VARCHAR, -- Online, Retail, B2B, Partner
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (sales_rep_id) REFERENCES sales_reps(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

-- Marketing campaigns table
CREATE TABLE marketing_campaigns (
    id INTEGER PRIMARY KEY,
    campaign_name VARCHAR,
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12,2),
    channel VARCHAR, -- Email, Social, PPC, TV, Radio
    target_region VARCHAR,
    target_demographic VARCHAR
);

-- Campaign performance tracking
CREATE TABLE campaign_performance (
    id INTEGER PRIMARY KEY,
    campaign_id INTEGER,
    date DATE,
    impressions INTEGER,
    clicks INTEGER,
    conversions INTEGER,
    cost DECIMAL(10,2),
    revenue DECIMAL(12,2),
    FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(id)
);

-- Generate synthetic companies
INSERT INTO companies 
WITH RECURSIVE company_generator(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM company_generator WHERE n < 50
)
SELECT 
    n as id,
    'Company ' || n as company_name,
    CASE (n % 8)
        WHEN 0 THEN 'Technology'
        WHEN 1 THEN 'Healthcare'
        WHEN 2 THEN 'Finance'
        WHEN 3 THEN 'Retail'
        WHEN 4 THEN 'Manufacturing'
        WHEN 5 THEN 'Energy'
        WHEN 6 THEN 'Media'
        ELSE 'Services'
    END as industry,
    1990 + (n % 35) as founded_year,
    1 + (n % 10) as headquarters_city_id,
    CASE 
        WHEN n % 4 = 0 THEN 'Enterprise'
        WHEN n % 4 = 1 THEN 'Large'
        WHEN n % 4 = 2 THEN 'Medium'
        ELSE 'Small'
    END as revenue_category,
    50 + (n * 23) % 5000 as employee_count
FROM company_generator;

-- Generate synthetic products
INSERT INTO products
WITH RECURSIVE product_generator(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM product_generator WHERE n < 200
)
SELECT 
    n as id,
    'Product ' || n as product_name,
    CASE (n % 5)
        WHEN 0 THEN 'Electronics'
        WHEN 1 THEN 'Clothing'
        WHEN 2 THEN 'Home & Garden'
        WHEN 3 THEN 'Sports'
        ELSE 'Books'
    END as category,
    CASE ((n * 7) % 15)
        WHEN 0 THEN 'Smartphones'
        WHEN 1 THEN 'Laptops'
        WHEN 2 THEN 'Tablets'
        WHEN 3 THEN 'Shirts'
        WHEN 4 THEN 'Pants'
        WHEN 5 THEN 'Shoes'
        WHEN 6 THEN 'Furniture'
        WHEN 7 THEN 'Tools'
        WHEN 8 THEN 'Appliances'
        WHEN 9 THEN 'Baseball'
        WHEN 10 THEN 'Basketball'
        WHEN 11 THEN 'Football'
        WHEN 12 THEN 'Fiction'
        WHEN 13 THEN 'Non-Fiction'
        ELSE 'Reference'
    END as subcategory,
    'Brand ' || ((n * 3) % 20 + 1) as brand,
    10.00 + (n * 17) % 500 as unit_cost,
    20.00 + (n * 23) % 1000 as unit_price,
    DATE '2020-01-01' + (n * 5) % 1460 as launch_date,
    CASE WHEN n % 10 = 0 THEN DATE '2024-06-01' + (n % 100) ELSE NULL END as discontinue_date
FROM product_generator;

-- Generate synthetic customers
INSERT INTO customers
WITH RECURSIVE customer_generator(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM customer_generator WHERE n < 1000
)
SELECT 
    n as id,
    'Customer ' || n as customer_name,
    CASE (n % 3)
        WHEN 0 THEN 'Individual'
        WHEN 1 THEN 'Small Business'
        ELSE 'Enterprise'
    END as customer_type,
    1 + (n % 10) as city_id,
    DATE '2020-01-01' + (n * 3) % 1460 as registration_date,
    300 + (n * 7) % 551 as credit_score,
    100.00 + (n * 47) % 50000 as lifetime_value
FROM customer_generator;

-- Generate synthetic sales reps
INSERT INTO sales_reps
WITH RECURSIVE rep_generator(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM rep_generator WHERE n < 25
)
SELECT 
    n as id,
    'Rep ' || n as rep_name,
    DATE '2018-01-01' + (n * 30) % 2190 as hire_date,
    CASE (n % 4)
        WHEN 0 THEN 'Northeast'
        WHEN 1 THEN 'South'
        WHEN 2 THEN 'Midwest'
        ELSE 'West'
    END as territory_region,
    CASE (n % 4)
        WHEN 0 THEN 'Junior'
        WHEN 1 THEN 'Senior'
        WHEN 2 THEN 'Expert'
        ELSE 'Director'
    END as performance_tier,
    100000.00 + (n * 15000) % 500000 as annual_quota
FROM rep_generator;

-- Generate synthetic transactions (10,000 records)
INSERT INTO transactions
WITH RECURSIVE transaction_generator(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM transaction_generator WHERE n < 10000
)
SELECT 
    n as id,
    DATE '2023-01-01' + (n % 545) as transaction_date,
    1 + (n * 7) % 1000 as customer_id,
    1 + (n * 11) % 25 as sales_rep_id,
    1 + (n * 13) % 200 as product_id,
    1 + (n * 17) % 10 as city_id,
    1 + (n * 3) % 10 as quantity,
    20.00 + (n * 23) % 1000 as unit_price,
    CASE WHEN n % 10 = 0 THEN (n % 20) ELSE 0 END as discount_percent,
    (20.00 + (n * 23) % 1000) * (1 + (n * 3) % 10) * (1 - CASE WHEN n % 10 = 0 THEN (n % 20) / 100.0 ELSE 0 END) as total_amount,
    CASE (n % 4)
        WHEN 0 THEN 'Credit Card'
        WHEN 1 THEN 'Cash'
        WHEN 2 THEN 'Check'
        ELSE 'Bank Transfer'
    END as payment_method,
    CASE (n % 4)
        WHEN 0 THEN 'Online'
        WHEN 1 THEN 'Retail'
        WHEN 2 THEN 'B2B'
        ELSE 'Partner'
    END as channel
FROM transaction_generator;

-- Generate marketing campaigns
INSERT INTO marketing_campaigns
WITH RECURSIVE campaign_generator(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM campaign_generator WHERE n < 20
)
SELECT 
    n as id,
    'Campaign ' || n as campaign_name,
    DATE '2023-01-01' + (n * 45) % 365 as start_date,
    DATE '2023-01-01' + (n * 45) % 365 + 30 as end_date,
    10000.00 + (n * 5000) % 100000 as budget,
    CASE (n % 5)
        WHEN 0 THEN 'Email'
        WHEN 1 THEN 'Social'
        WHEN 2 THEN 'PPC'
        WHEN 3 THEN 'TV'
        ELSE 'Radio'
    END as channel,
    CASE (n % 4)
        WHEN 0 THEN 'Northeast'
        WHEN 1 THEN 'South'
        WHEN 2 THEN 'Midwest'
        ELSE 'West'
    END as target_region,
    CASE (n % 6)
        WHEN 0 THEN '18-25'
        WHEN 1 THEN '26-35'
        WHEN 2 THEN '36-45'
        WHEN 3 THEN '46-55'
        WHEN 4 THEN '56-65'
        ELSE '65+'
    END as target_demographic
FROM campaign_generator;

-- Generate campaign performance data
INSERT INTO campaign_performance
WITH RECURSIVE perf_generator(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM perf_generator WHERE n < 600
)
SELECT 
    n as id,
    1 + (n % 20) as campaign_id,
    DATE '2023-01-01' + (n % 365) as date,
    1000 + (n * 137) % 10000 as impressions,
    10 + (n * 23) % 500 as clicks,
    1 + (n * 7) % 50 as conversions,
    50.00 + (n * 13) % 1000 as cost,
    100.00 + (n * 29) % 5000 as revenue
FROM perf_generator;

-- Create comprehensive business views
CREATE VIEW sales_performance AS
SELECT 
    sr.rep_name,
    sr.territory_region,
    sr.performance_tier,
    COUNT(t.id) as total_transactions,
    SUM(t.total_amount) as total_sales,
    AVG(t.total_amount) as avg_transaction_size,
    SUM(t.quantity) as total_units_sold
FROM sales_reps sr
LEFT JOIN transactions t ON sr.id = t.sales_rep_id
GROUP BY sr.id, sr.rep_name, sr.territory_region, sr.performance_tier;

CREATE VIEW product_performance AS
SELECT 
    p.product_name,
    p.category,
    p.subcategory,
    p.brand,
    COUNT(t.id) as transaction_count,
    SUM(t.quantity) as units_sold,
    SUM(t.total_amount) as total_revenue,
    AVG(t.unit_price) as avg_selling_price,
    p.unit_cost,
    SUM(t.total_amount) - (SUM(t.quantity) * p.unit_cost) as gross_profit
FROM products p
LEFT JOIN transactions t ON p.id = t.product_id
GROUP BY p.id, p.product_name, p.category, p.subcategory, p.brand, p.unit_cost;

CREATE VIEW regional_analysis AS
SELECT 
    c.region,
    c.state_abrv,
    c.city_name,
    COUNT(DISTINCT cu.id) as customer_count,
    COUNT(t.id) as transaction_count,
    SUM(t.total_amount) as total_revenue,
    AVG(t.total_amount) as avg_transaction_value,
    SUM(t.quantity) as total_units_sold
FROM cities c
LEFT JOIN customers cu ON c.id = cu.city_id
LEFT JOIN transactions t ON c.id = t.city_id
GROUP BY c.id, c.region, c.state_abrv, c.city_name;

CREATE VIEW customer_segmentation AS
SELECT 
    cu.customer_type,
    COUNT(cu.id) as customer_count,
    COUNT(t.id) as total_transactions,
    SUM(t.total_amount) as total_revenue,
    AVG(t.total_amount) as avg_transaction_value,
    AVG(cu.lifetime_value) as avg_lifetime_value,
    AVG(cu.credit_score) as avg_credit_score
FROM customers cu
LEFT JOIN transactions t ON cu.id = t.customer_id
GROUP BY cu.customer_type;