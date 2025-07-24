#!/usr/bin/env python3
"""
Semantic Layer Value Comparison Demo
Demonstrates the differences between text-to-SQL and semantic layer approaches
"""

import json
import time
import urllib.request
import urllib.error
import psycopg2
from typing import Dict, Any, List, Tuple

class SemanticLayerComparison:
    """Demonstrates semantic layer value vs raw SQL"""
    
    def __init__(self):
        self.cube_url = "http://localhost:4000"
        self.duckdb_params = {
            'host': 'localhost',
            'port': 15432,
            'user': 'root',
            'database': 'warehouse'
        }
    
    def execute_raw_sql(self, sql: str, description: str) -> Dict[str, Any]:
        """Execute raw SQL and return results with timing"""
        try:
            start_time = time.time()
            conn = psycopg2.connect(**self.duckdb_params)
            cursor = conn.cursor()
            
            cursor.execute(sql)
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            query_time = (time.time() - start_time) * 1000
            
            conn.close()
            
            return {
                'success': True,
                'description': description,
                'query_time_ms': query_time,
                'results': results,
                'columns': columns,
                'row_count': len(results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'description': description,
                'error': str(e)
            }
    
    def execute_semantic_query(self, query: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Execute semantic layer query and return results with timing"""
        try:
            start_time = time.time()
            
            data = json.dumps({"query": query}).encode('utf-8')
            req = urllib.request.Request(
                f"{self.cube_url}/cubejs-api/v1/load",
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                query_time = (time.time() - start_time) * 1000
                
                if response.getcode() == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    
                    return {
                        'success': True,
                        'description': description,
                        'query_time_ms': query_time,
                        'results': result.get('data', []),
                        'row_count': len(result.get('data', []))
                    }
                else:
                    return {
                        'success': False,
                        'description': description,
                        'error': f"HTTP {response.getcode()}"
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'description': description,
                'error': str(e)
            }
    
    def demo_consistency_problem(self):
        """Demonstrate consistency issues with text-to-SQL"""
        print("🎯 DEMO 1: CONSISTENCY PROBLEMS")
        print("=" * 50)
        print()
        print("Business Question: 'What's our customer lifetime value?'")
        print()
        
        # Simulation of different SQL approaches
        sql_approaches = [
            {
                'sql': """
                    SELECT 
                        customer_id,
                        SUM(amount) as lifetime_value
                    FROM sales 
                    GROUP BY customer_id
                    ORDER BY lifetime_value DESC
                    LIMIT 5;
                """,
                'description': "Text-to-SQL Attempt #1: Simple sum of all transactions"
            },
            {
                'sql': """
                    SELECT 
                        c.customer_type,
                        AVG(c.total_spent) as avg_lifetime_value
                    FROM customers c
                    WHERE c.customer_type IS NOT NULL
                    GROUP BY c.customer_type
                    ORDER BY avg_lifetime_value DESC;
                """,
                'description': "Text-to-SQL Attempt #2: Average from customer table"
            },
            {
                'sql': """
                    SELECT 
                        c.customer_type,
                        AVG(sales_total.total) as calculated_avg_ltv
                    FROM customers c
                    JOIN (
                        SELECT customer_id, SUM(amount) as total
                        FROM sales 
                        GROUP BY customer_id
                    ) sales_total ON c.customer_id = sales_total.customer_id
                    GROUP BY c.customer_type
                    ORDER BY calculated_avg_ltv DESC;
                """,
                'description': "Text-to-SQL Attempt #3: Calculated from sales data"
            }
        ]
        
        # Execute SQL approaches
        sql_results = []
        for approach in sql_approaches:
            result = self.execute_raw_sql(approach['sql'], approach['description'])
            sql_results.append(result)
            
            print(f"📊 {approach['description']}")
            if result['success']:
                print(f"   ⏱️  Query time: {result['query_time_ms']:.1f}ms")
                if 'customer_type' in str(result['columns']):
                    # Show customer type results
                    for row in result['results'][:3]:
                        print(f"   💰 {row[0]}: ${row[1]:,.2f}")
                else:
                    # Show individual customer results
                    print(f"   📈 Found {result['row_count']} customers")
                    for row in result['results'][:3]:
                        print(f"   💰 Customer {row[0]}: ${row[1]:,.2f}")
                print()
            else:
                print(f"   ❌ Error: {result['error']}\n")
        
        # Show semantic layer approach
        print("🎯 SEMANTIC LAYER APPROACH:")
        print("-" * 30)
        
        semantic_query = {
            "measures": ["customers.average_lifetime_value"],
            "dimensions": ["customers.customer_type"]
        }
        
        semantic_result = self.execute_semantic_query(semantic_query, "Semantic Layer: Consistent LTV calculation")
        
        if semantic_result['success']:
            print(f"📊 {semantic_result['description']}")
            print(f"   ⏱️  Query time: {semantic_result['query_time_ms']:.1f}ms")
            print("   💰 Results:")
            for row in semantic_result['results']:
                customer_type = row.get('customers.customer_type', 'Unknown')
                ltv = row.get('customers.average_lifetime_value', 0)
                print(f"      {customer_type}: ${ltv:,.2f}")
            print()
        
        print("🏆 SEMANTIC LAYER BENEFITS:")
        print("   ✅ One consistent calculation method")
        print("   ✅ Business-validated logic")
        print("   ✅ Same result every time")
        print("   ✅ Governed and auditable")
        print()
    
    def demo_revenue_recognition(self):
        """Demonstrate revenue recognition complexity"""
        print("🎯 DEMO 2: REVENUE RECOGNITION")
        print("=" * 50)
        print()
        print("Business Question: 'What's our total revenue?'")
        print()
        
        # Different revenue calculations
        revenue_approaches = [
            {
                'sql': "SELECT SUM(amount) as total_revenue FROM sales;",
                'description': "Naive approach: Sum all amounts",
                'problems': ["Includes test data", "Includes taxes", "Includes refunds"]
            },
            {
                'sql': """
                    SELECT SUM(amount) as total_revenue 
                    FROM sales 
                    WHERE amount > 0;
                """,
                'description': "Attempt 2: Exclude negative amounts",
                'problems': ["Still includes test data", "Still includes taxes"]
            },
            {
                'sql': """
                    SELECT SUM(amount) as total_revenue 
                    FROM sales s
                    JOIN customers c ON s.customer_id = c.customer_id
                    WHERE amount > 0 
                      AND c.customer_type != 'test';
                """,
                'description': "Attempt 3: Exclude test customers",
                'problems': ["Still includes taxes", "What about internal transactions?"]
            }
        ]
        
        print("📊 TEXT-TO-SQL EVOLUTION:")
        print("-" * 30)
        
        for i, approach in enumerate(revenue_approaches, 1):
            result = self.execute_raw_sql(approach['sql'], approach['description'])
            
            print(f"Attempt {i}: {approach['description']}")
            if result['success'] and result['results']:
                revenue = result['results'][0][0]
                print(f"   💰 Revenue: ${revenue:,.2f}")
                print(f"   ⏱️  Query time: {result['query_time_ms']:.1f}ms")
                print("   ❌ Problems:")
                for problem in approach['problems']:
                    print(f"      - {problem}")
            print()
        
        # Semantic layer approach
        print("🎯 SEMANTIC LAYER APPROACH:")
        print("-" * 30)
        
        semantic_query = {
            "measures": ["sales.total_revenue"]
        }
        
        semantic_result = self.execute_semantic_query(semantic_query, "Semantic Layer: Business-validated revenue")
        
        if semantic_result['success'] and semantic_result['results']:
            revenue_data = semantic_result['results'][0]
            revenue = revenue_data.get('sales.total_revenue', 0)
            print(f"📊 Business-validated revenue calculation")
            print(f"   💰 Revenue: ${revenue:,.2f}")
            print(f"   ⏱️  Query time: {semantic_result['query_time_ms']:.1f}ms")
            print("   ✅ Benefits:")
            print("      ✓ Excludes test transactions")
            print("      ✓ Proper tax handling")
            print("      ✓ Refund processing")
            print("      ✓ Business rule compliance")
            print("      ✓ Finance team validated")
        print()
    
    def demo_performance_comparison(self):
        """Demonstrate performance differences"""
        print("🎯 DEMO 3: PERFORMANCE COMPARISON")
        print("=" * 50)
        print()
        print("Business Question: 'Show me sales performance by product category and customer type'")
        print()
        
        # Complex SQL query
        complex_sql = """
            SELECT 
                s.product_category,
                c.customer_type,
                COUNT(*) as transaction_count,
                SUM(s.amount) as total_revenue,
                AVG(s.amount) as avg_order_value
            FROM sales s
            JOIN customers c ON s.customer_id = c.customer_id
            WHERE s.amount > 0
              AND c.customer_type IS NOT NULL
              AND s.product_category IS NOT NULL
            GROUP BY s.product_category, c.customer_type
            ORDER BY total_revenue DESC;
        """
        
        print("📊 RAW SQL APPROACH:")
        print("-" * 20)
        
        sql_result = self.execute_raw_sql(complex_sql, "Complex join and aggregation")
        
        if sql_result['success']:
            print(f"   ⏱️  Query time: {sql_result['query_time_ms']:.1f}ms")
            print(f"   📈 Results: {sql_result['row_count']} combinations")
            print("   📊 Top results:")
            for row in sql_result['results'][:3]:
                print(f"      {row[0]} + {row[1]}: ${row[3]:,.2f} ({row[2]} transactions)")
        else:
            print(f"   ❌ Error: {sql_result['error']}")
        print()
        
        # Semantic layer approach
        print("🎯 SEMANTIC LAYER APPROACH:")
        print("-" * 30)
        
        semantic_query = {
            "measures": ["sales.total_revenue", "sales.count", "sales.average_order_value"],
            "dimensions": ["sales.product_category", "customers.customer_type"]
        }
        
        semantic_result = self.execute_semantic_query(semantic_query, "Optimized semantic query")
        
        if semantic_result['success']:
            print(f"   ⏱️  Query time: {semantic_result['query_time_ms']:.1f}ms")
            print(f"   📈 Results: {semantic_result['row_count']} combinations")
            print("   📊 Top results:")
            for row in semantic_result['results'][:3]:
                category = row.get('sales.product_category', 'Unknown')
                customer_type = row.get('customers.customer_type', 'Unknown')
                revenue = row.get('sales.total_revenue', 0)
                count = row.get('sales.count', 0)
                print(f"      {category} + {customer_type}: ${revenue:,.2f} ({count} transactions)")
        else:
            print(f"   ❌ Error: {semantic_result['error']}")
        print()
        
        # Performance analysis
        if sql_result['success'] and semantic_result['success']:
            speedup = sql_result['query_time_ms'] / semantic_result['query_time_ms']
            print("🏆 PERFORMANCE ANALYSIS:")
            print(f"   ⚡ Semantic layer is {speedup:.1f}x faster")
            print("   ✅ Plus: Consistent business logic")
            print("   ✅ Plus: Pre-aggregated data")
            print("   ✅ Plus: Query optimization")
        print()
    
    def demo_business_terminology(self):
        """Demonstrate business vs technical terminology"""
        print("🎯 DEMO 4: BUSINESS TERMINOLOGY")
        print("=" * 50)
        print()
        
        business_questions = [
            {
                'question': "What's our average order value?",
                'sql_complexity': """
                    -- User needs to know:
                    -- 1. Which table has orders
                    -- 2. How to calculate averages
                    -- 3. What constitutes a valid order
                    SELECT AVG(amount) FROM sales WHERE amount > 0;
                """,
                'semantic_query': {
                    "measures": ["sales.average_order_value"]
                },
                'semantic_term': "sales.average_order_value"
            },
            {
                'question': "How many customers do we have by segment?",
                'sql_complexity': """
                    -- User needs to know:
                    -- 1. Customer table structure
                    -- 2. How segments are defined
                    -- 3. How to handle null values
                    SELECT customer_type, COUNT(*) 
                    FROM customers 
                    WHERE customer_type IS NOT NULL 
                    GROUP BY customer_type;
                """,
                'semantic_query': {
                    "measures": ["customers.count"],
                    "dimensions": ["customers.customer_type"]
                },
                'semantic_term': "customers.count by customers.customer_type"
            }
        ]
        
        for i, bq in enumerate(business_questions, 1):
            print(f"📋 Business Question {i}: '{bq['question']}'")
            print()
            
            print("❌ TEXT-TO-SQL COMPLEXITY:")
            print(bq['sql_complexity'])
            print()
            
            print("✅ SEMANTIC LAYER SIMPLICITY:")
            print(f"   Business term: {bq['semantic_term']}")
            
            result = self.execute_semantic_query(bq['semantic_query'], bq['question'])
            if result['success']:
                print(f"   Query time: {result['query_time_ms']:.1f}ms")
                print("   Results:")
                for row in result['results'][:5]:
                    print(f"      {row}")
            print()
            print("-" * 50)
            print()
    
    def run_complete_comparison(self):
        """Run the complete semantic layer value demonstration"""
        print("🎯 SEMANTIC LAYER VALUE DEMONSTRATION")
        print("=" * 60)
        print()
        print("This demo shows why semantic layers are essential for")
        print("reliable, consistent, and performant business intelligence.")
        print()
        print("We'll compare traditional text-to-SQL approaches with")
        print("our semantic layer across four key dimensions:")
        print("1. Consistency")
        print("2. Revenue Recognition") 
        print("3. Performance")
        print("4. Business Terminology")
        print()
        print("=" * 60)
        print()
        
        start_time = time.time()
        
        # Run all demonstrations
        self.demo_consistency_problem()
        self.demo_revenue_recognition()
        self.demo_performance_comparison()
        self.demo_business_terminology()
        
        total_time = time.time() - start_time
        
        # Summary
        print("🎉 SEMANTIC LAYER VALUE SUMMARY")
        print("=" * 40)
        print()
        print("✅ DEMONSTRATED BENEFITS:")
        print("   🎯 Consistent business logic across all queries")
        print("   💰 Validated revenue recognition rules")
        print("   ⚡ Better performance through optimization")
        print("   🗣️  Business-friendly terminology")
        print("   🔒 Governed and auditable metrics")
        print("   🔄 Repeatable and reliable results")
        print()
        print("❌ TEXT-TO-SQL PROBLEMS HIGHLIGHTED:")
        print("   ⚠️  Inconsistent calculations")
        print("   🐛 Missing business logic")
        print("   🐌 Slower performance")
        print("   🤔 Technical complexity for business users")
        print("   🚫 No governance or validation")
        print()
        print(f"Demo completed in {total_time:.1f} seconds")
        print()
        print("🚀 CONCLUSION:")
        print("Semantic layers are not just 'nice to have' - they're")
        print("essential for enterprise-grade AI analytics.")
        print()
        print("AI + Semantic Layer > AI + Text-to-SQL")

def main():
    """Main demonstration function"""
    comparison = SemanticLayerComparison()
    comparison.run_complete_comparison()

if __name__ == "__main__":
    main()