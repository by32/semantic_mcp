#!/usr/bin/env python3
"""
Demo Validation Script
Tests all queries and scenarios used in the demo to ensure they work correctly
"""

import json
import sys
import time
import urllib.request
import urllib.error
import psycopg2
from typing import Dict, Any, List, Optional

class DemoValidator:
    """Validates all demo scenarios and queries"""
    
    def __init__(self):
        self.cube_url = "http://localhost:4000"
        self.duckdb_params = {
            'host': 'localhost',
            'port': 15432,
            'user': 'root',
            'database': 'warehouse'
        }
        self.results = []
        
    def log_result(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.results.append({
            'test': test_name,
            'success': success,
            'message': message,
            'data': data
        })
    
    def test_tier1_object_storage(self) -> bool:
        """Test Tier 1: Object Storage Layer"""
        print("\n" + "="*50)
        print("TIER 1: Object Storage Layer")
        print("="*50)
        
        # Test MinIO accessibility (basic connectivity)
        try:
            # Test MinIO health endpoint
            req = urllib.request.Request("http://localhost:9001/minio/health/live")
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 200:
                    self.log_result("MinIO Health Check", True, "MinIO is accessible")
                    return True
                else:
                    self.log_result("MinIO Health Check", False, f"HTTP {response.getcode()}")
                    return False
        except Exception as e:
            self.log_result("MinIO Health Check", False, f"Cannot connect to MinIO: {e}")
            return False
    
    def test_tier2_duckdb_analytics(self) -> bool:
        """Test Tier 2: DuckDB Analytics Engine"""
        print("\n" + "="*50)
        print("TIER 2: DuckDB Analytics Engine")
        print("="*50)
        
        try:
            # Connect to DuckDB
            conn = psycopg2.connect(**self.duckdb_params)
            cursor = conn.cursor()
            
            # Test 1: Show tables
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            table_names = [table[0] for table in tables]
            
            expected_tables = ['cities', 'sales', 'customers']
            missing_tables = [t for t in expected_tables if t not in table_names]
            
            if not missing_tables:
                self.log_result("DuckDB Tables", True, f"Found all tables: {table_names}")
            else:
                self.log_result("DuckDB Tables", False, f"Missing tables: {missing_tables}")
                return False
            
            # Test 2: Cities query
            start_time = time.time()
            cursor.execute("""
                SELECT 
                    region,
                    COUNT(*) as city_count,
                    SUM(population) as total_population
                FROM cities 
                GROUP BY region 
                ORDER BY total_population DESC;
            """)
            cities_result = cursor.fetchall()
            cities_time = (time.time() - start_time) * 1000
            
            if cities_result:
                self.log_result("Cities Analytics Query", True, 
                              f"Query time: {cities_time:.2f}ms, Results: {len(cities_result)} regions")
            else:
                self.log_result("Cities Analytics Query", False, "No results returned")
            
            # Test 3: Sales query
            start_time = time.time()
            cursor.execute("""
                SELECT 
                    product_category,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_revenue,
                    AVG(amount) as avg_order_value
                FROM sales 
                GROUP BY product_category 
                ORDER BY total_revenue DESC;
            """)
            sales_result = cursor.fetchall()
            sales_time = (time.time() - start_time) * 1000
            
            if sales_result:
                self.log_result("Sales Analytics Query", True, 
                              f"Query time: {sales_time:.2f}ms, Results: {len(sales_result)} categories")
            else:
                self.log_result("Sales Analytics Query", False, "No results returned")
            
            # Test 4: Cross-table join
            start_time = time.time()
            cursor.execute("""
                SELECT 
                    c.customer_type,
                    COUNT(s.transaction_id) as transactions,
                    SUM(s.amount) as total_spent
                FROM customers c
                JOIN sales s ON c.customer_id = s.customer_id
                GROUP BY c.customer_type
                ORDER BY total_spent DESC;
            """)
            join_result = cursor.fetchall()
            join_time = (time.time() - start_time) * 1000
            
            if join_result:
                self.log_result("Cross-table Join Query", True, 
                              f"Query time: {join_time:.2f}ms, Results: {len(join_result)} customer types")
            else:
                self.log_result("Cross-table Join Query", False, "No results returned")
            
            conn.close()
            return True
            
        except Exception as e:
            self.log_result("DuckDB Connection", False, f"Database error: {e}")
            return False
    
    def test_tier3_cube_semantic_layer(self) -> bool:
        """Test Tier 3: Cube.dev Semantic Layer"""
        print("\n" + "="*50)
        print("TIER 3: Cube.dev Semantic Layer")
        print("="*50)
        
        # Test 1: Cube.dev health
        try:
            req = urllib.request.Request(f"{self.cube_url}/cubejs-api/v1/meta")
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    meta_data = json.loads(response.read().decode('utf-8'))
                    cubes = meta_data.get('cubes', [])
                    cube_names = [cube['name'] for cube in cubes]
                    
                    expected_cubes = ['cities', 'sales', 'customers']
                    missing_cubes = [c for c in expected_cubes if c not in cube_names]
                    
                    if not missing_cubes:
                        self.log_result("Cube.dev Schema", True, f"Found all cubes: {cube_names}")
                    else:
                        self.log_result("Cube.dev Schema", False, f"Missing cubes: {missing_cubes}")
                        return False
                else:
                    self.log_result("Cube.dev Health", False, f"HTTP {response.getcode()}")
                    return False
        except Exception as e:
            self.log_result("Cube.dev Health", False, f"Cannot connect to Cube.dev: {e}")
            return False
        
        # Test 2: Geographic Analysis Query
        geographic_query = {
            "measures": ["cities.total_population"],
            "dimensions": ["cities.city_name", "cities.region"],
            "order": {"cities.total_population": "desc"},
            "limit": 10
        }
        
        success = self._test_cube_query("Geographic Analysis", geographic_query)
        if not success:
            return False
        
        # Test 3: Sales Performance Query
        sales_query = {
            "measures": ["sales.total_revenue", "sales.count"],
            "dimensions": ["sales.product_category"],
            "order": {"sales.total_revenue": "desc"}
        }
        
        success = self._test_cube_query("Sales Performance", sales_query)
        if not success:
            return False
        
        # Test 4: Customer Segmentation Query
        customer_query = {
            "measures": ["customers.count", "customers.average_lifetime_value"],
            "dimensions": ["customers.customer_type", "customers.credit_score_tier"]
        }
        
        success = self._test_cube_query("Customer Segmentation", customer_query)
        if not success:
            return False
        
        return True
    
    def _test_cube_query(self, query_name: str, query: Dict[str, Any]) -> bool:
        """Test a specific Cube.dev query"""
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
                    
                    if 'data' in result:
                        row_count = len(result['data'])
                        self.log_result(f"Cube.dev {query_name}", True, 
                                      f"Query time: {query_time:.2f}ms, Results: {row_count} rows")
                        return True
                    else:
                        self.log_result(f"Cube.dev {query_name}", False, "No data in response")
                        return False
                else:
                    self.log_result(f"Cube.dev {query_name}", False, f"HTTP {response.getcode()}")
                    return False
                    
        except Exception as e:
            self.log_result(f"Cube.dev {query_name}", False, f"Query error: {e}")
            return False
    
    def test_tier4_mcp_integration(self) -> bool:
        """Test Tier 4: MCP Integration"""
        print("\n" + "="*50)
        print("TIER 4: MCP Integration")
        print("="*50)
        
        # For this test, we'll import and test the MCP server directly
        try:
            # Test MCP server import
            import semantic_mcp_server
            self.log_result("MCP Server Import", True, "MCP server module loaded successfully")
            
            # Test MCP tools availability
            # Note: This would require running the MCP server in a subprocess
            # For now, we'll just verify the module has the expected functions
            if hasattr(semantic_mcp_server, 'query_semantic_layer'):
                self.log_result("MCP Tools Available", True, "MCP tools functions found")
            else:
                self.log_result("MCP Tools Available", False, "MCP tools functions missing")
                return False
                
            return True
            
        except ImportError as e:
            self.log_result("MCP Server Import", False, f"Cannot import MCP server: {e}")
            return False
        except Exception as e:
            self.log_result("MCP Integration", False, f"MCP test error: {e}")
            return False
    
    def test_tier5_demo_queries(self) -> bool:
        """Test Tier 5: Demo Natural Language Queries"""
        print("\n" + "="*50)
        print("TIER 5: Demo Natural Language Queries")
        print("="*50)
        
        # Test the queries used in the demo through Cube.dev API
        demo_queries = [
            {
                "name": "Top 5 Cities by Population",
                "description": "What are the top 5 most populous cities?",
                "query": {
                    "measures": ["cities.total_population"],
                    "dimensions": ["cities.city_name", "cities.state_name"],
                    "order": {"cities.total_population": "desc"},
                    "limit": 5
                }
            },
            {
                "name": "Revenue by Product Category",
                "description": "Show me revenue by product category",
                "query": {
                    "measures": ["sales.total_revenue"],
                    "dimensions": ["sales.product_category"],
                    "order": {"sales.total_revenue": "desc"}
                }
            },
            {
                "name": "Customer Lifetime Value by Type",
                "description": "Which customer types have the highest lifetime value?",
                "query": {
                    "measures": ["customers.average_lifetime_value", "customers.count"],
                    "dimensions": ["customers.customer_type"],
                    "order": {"customers.average_lifetime_value": "desc"}
                }
            },
            {
                "name": "Sales Performance Overview",
                "description": "Show me overall sales performance",
                "query": {
                    "measures": ["sales.total_revenue", "sales.count", "sales.average_order_value"],
                    "dimensions": ["sales.product_category"],
                    "order": {"sales.total_revenue": "desc"}
                }
            }
        ]
        
        all_passed = True
        for demo_query in demo_queries:
            success = self._test_cube_query(demo_query["name"], demo_query["query"])
            if not success:
                all_passed = False
        
        return all_passed
    
    def run_complete_validation(self) -> bool:
        """Run complete demo validation"""
        print("🧪 SEMANTIC MCP DEMO VALIDATION")
        print("="*60)
        
        start_time = time.time()
        
        # Run all tier tests
        tier1_pass = self.test_tier1_object_storage()
        tier2_pass = self.test_tier2_duckdb_analytics()
        tier3_pass = self.test_tier3_cube_semantic_layer()
        tier4_pass = self.test_tier4_mcp_integration()
        tier5_pass = self.test_tier5_demo_queries()
        
        total_time = time.time() - start_time
        
        # Summary
        print("\n" + "="*60)
        print("DEMO VALIDATION SUMMARY")
        print("="*60)
        
        tier_results = [
            ("Tier 1: Object Storage", tier1_pass),
            ("Tier 2: DuckDB Analytics", tier2_pass),
            ("Tier 3: Cube.dev Semantic Layer", tier3_pass),
            ("Tier 4: MCP Integration", tier4_pass),
            ("Tier 5: Demo Queries", tier5_pass)
        ]
        
        passed_count = sum(1 for _, passed in tier_results if passed)
        total_count = len(tier_results)
        
        for tier_name, passed in tier_results:
            status = "✅ READY" if passed else "❌ FAILED"
            print(f"{status} {tier_name}")
        
        print(f"\nOverall: {passed_count}/{total_count} tiers passed")
        print(f"Validation time: {total_time:.2f} seconds")
        
        # Individual test summary
        test_passed = sum(1 for result in self.results if result['success'])
        test_total = len(self.results)
        print(f"Individual tests: {test_passed}/{test_total} passed")
        
        all_passed = all(passed for _, passed in tier_results)
        
        if all_passed:
            print("\n🎉 DEMO IS READY FOR PRESENTATION!")
            print("All tiers are functioning correctly.")
        else:
            print("\n⚠️  DEMO NEEDS ATTENTION")
            print("Some tiers failed validation. Check the logs above.")
        
        return all_passed
    
    def generate_demo_report(self) -> str:
        """Generate a demo readiness report"""
        report = []
        report.append("# Demo Validation Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for result in self.results:
            status = "✅" if result['success'] else "❌"
            report.append(f"{status} **{result['test']}**: {result['message']}")
        
        return "\n".join(report)

def main():
    """Main validation function"""
    validator = DemoValidator()
    
    # Run validation
    success = validator.run_complete_validation()
    
    # Generate report
    report = validator.generate_demo_report()
    
    # Save report
    with open('/tmp/demo_validation_report.md', 'w') as f:
        f.write(report)
    
    print(f"\n📊 Detailed report saved to: /tmp/demo_validation_report.md")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()