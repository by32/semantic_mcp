-- Create sample data tables for the semantic layer
CREATE TABLE cities (
    id INTEGER PRIMARY KEY,
    city_name VARCHAR,
    state_abrv VARCHAR,
    state_name VARCHAR,
    population INTEGER,
    area_sq_miles REAL,
    founded_year INTEGER,
    region VARCHAR
);

CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    city_id INTEGER,
    date DATE,
    product_category VARCHAR,
    sales_amount DECIMAL(10,2),
    units_sold INTEGER,
    sales_rep VARCHAR,
    FOREIGN KEY (city_id) REFERENCES cities(id)
);

-- Insert sample city data
INSERT INTO cities VALUES
(1, 'New York', 'NY', 'New York', 8336817, 302.6, 1624, 'Northeast'),
(2, 'Los Angeles', 'CA', 'California', 3979576, 468.7, 1781, 'West'),
(3, 'Chicago', 'IL', 'Illinois', 2693976, 227.6, 1833, 'Midwest'),
(4, 'Houston', 'TX', 'Texas', 2320268, 669.1, 1836, 'South'),
(5, 'Phoenix', 'AZ', 'Arizona', 1680992, 517.6, 1868, 'West'),
(6, 'Philadelphia', 'PA', 'Pennsylvania', 1584064, 134.1, 1682, 'Northeast'),
(7, 'San Antonio', 'TX', 'Texas', 1547253, 460.9, 1718, 'South'),
(8, 'San Diego', 'CA', 'California', 1423851, 325.2, 1769, 'West'),
(9, 'Dallas', 'TX', 'Texas', 1343573, 340.5, 1841, 'South'),
(10, 'San Jose', 'CA', 'California', 1021795, 176.5, 1777, 'West');

-- Insert sample sales data
INSERT INTO sales VALUES
(1, 1, '2024-01-15', 'Electronics', 15000.00, 25, 'Alice Johnson'),
(2, 1, '2024-01-20', 'Clothing', 8500.00, 40, 'Bob Smith'),
(3, 2, '2024-01-18', 'Electronics', 22000.00, 35, 'Carol Davis'),
(4, 2, '2024-01-25', 'Home & Garden', 12000.00, 30, 'David Wilson'),
(5, 3, '2024-02-01', 'Electronics', 18000.00, 28, 'Eve Brown'),
(6, 3, '2024-02-05', 'Clothing', 9500.00, 45, 'Frank Miller'),
(7, 4, '2024-02-10', 'Home & Garden', 14000.00, 35, 'Grace Lee'),
(8, 4, '2024-02-15', 'Electronics', 25000.00, 40, 'Henry Taylor'),
(9, 5, '2024-02-20', 'Clothing', 7500.00, 35, 'Ivy Anderson'),
(10, 5, '2024-02-25', 'Electronics', 20000.00, 32, 'Jack Thomas'),
(11, 6, '2024-03-01', 'Home & Garden', 16000.00, 40, 'Kelly White'),
(12, 6, '2024-03-05', 'Electronics', 19000.00, 30, 'Liam Garcia'),
(13, 7, '2024-03-10', 'Clothing', 11000.00, 50, 'Maya Rodriguez'),
(14, 7, '2024-03-15', 'Electronics', 23000.00, 38, 'Noah Martinez'),
(15, 8, '2024-03-20', 'Home & Garden', 13500.00, 32, 'Olivia Lopez'),
(16, 8, '2024-03-25', 'Electronics', 21000.00, 34, 'Paul Gonzalez'),
(17, 9, '2024-04-01', 'Clothing', 8800.00, 42, 'Quinn Perez'),
(18, 9, '2024-04-05', 'Electronics', 24000.00, 36, 'Ruby Wilson'),
(19, 10, '2024-04-10', 'Home & Garden', 15500.00, 38, 'Sam Johnson'),
(20, 10, '2024-04-15', 'Electronics', 26000.00, 42, 'Tina Davis');

-- Create some views for easier querying
CREATE VIEW city_sales_summary AS
SELECT 
    c.city_name,
    c.state_abrv,
    c.region,
    c.population,
    COUNT(s.id) as total_transactions,
    SUM(s.sales_amount) as total_sales,
    SUM(s.units_sold) as total_units,
    AVG(s.sales_amount) as avg_sale_amount
FROM cities c
LEFT JOIN sales s ON c.id = s.city_id
GROUP BY c.id, c.city_name, c.state_abrv, c.region, c.population;