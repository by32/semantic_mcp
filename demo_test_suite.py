#!/usr/bin/env python3
"""
Comprehensive Test Suite for DuckLake Semantic Layer MCP Demo

This test suite demonstrates the full capabilities of the semantic layer
for agentic AI platforms, showing natural language to data insights.
"""

import asyncio
import json
import httpx
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestCase:
    """Represents a single test case for the semantic layer"""
    name: str
    category: str
    natural_language: str
    expected_query: Dict[str, Any]
    description: str
    business_value: str
    difficulty_level: str  # "basic", "intermediate", "advanced"


@dataclass
class TestResult:
    """Results from executing a test case"""
    test_case: TestCase
    success: bool
    execution_time_ms: float
    result_data: Optional[List[Dict[str, Any]]] = None
    error_message: Optional[str] = None
    insights: Optional[str] = None


class SemanticLayerDemo:
    """Comprehensive demo and test suite for the semantic layer"""
    
    def __init__(self, base_url: str = "http://localhost:4000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        
    async def close(self):
        await self.client.aclose()
    
    def get_demo_test_cases(self) -> List[TestCase]:
        """Define comprehensive test cases for AI agent demos"""
        return [
            # ===== BASIC QUERIES =====
            TestCase(
                name="basic_population_ranking",
                category="Geographic Analysis",
                natural_language="What are the top 5 most populous cities?",
                expected_query={
                    "measures": ["cities.total_population"],
                    "dimensions": ["cities.city_name", "cities.state_name"],
                    "order": {"cities.total_population": "desc"},
                    "limit": 5
                },
                description="Identify the largest cities by population",
                business_value="Urban planning, market sizing, resource allocation",
                difficulty_level="basic"
            ),
            
            TestCase(
                name="regional_distribution",
                category="Geographic Analysis", 
                natural_language="How many cities are in each region?",
                expected_query={
                    "measures": ["cities.count"],
                    "dimensions": ["cities.region"],
                    "order": {"cities.count": "desc"}
                },
                description="Regional distribution of cities",
                business_value="Market expansion strategy, regional coverage analysis",
                difficulty_level="basic"
            ),
            
            # ===== CUSTOMER INSIGHTS =====
            TestCase(
                name="customer_segmentation",
                category="Customer Analytics",
                natural_language="Show customer distribution by type and credit score tier",
                expected_query={
                    "measures": ["customers.count", "customers.average_lifetime_value"],
                    "dimensions": ["customers.customer_type", "customers.credit_score_tier"]
                },
                description="Customer segmentation analysis",
                business_value="Target marketing, risk assessment, customer strategy",
                difficulty_level="intermediate"
            ),
            
            TestCase(
                name="high_value_customers",
                category="Customer Analytics",
                natural_language="Which customer types have the highest lifetime value?",
                expected_query={
                    "measures": ["customers.average_lifetime_value", "customers.count"],
                    "dimensions": ["customers.customer_type"],
                    "order": {"customers.average_lifetime_value": "desc"}
                },
                description="Identify most valuable customer segments",
                business_value="Customer acquisition cost optimization, retention strategy",
                difficulty_level="intermediate"
            ),
            
            # ===== SALES PERFORMANCE =====
            TestCase(
                name="revenue_by_category",
                category="Sales Analytics",
                natural_language="What product categories generate the most revenue?",
                expected_query={
                    "measures": ["sales.total_revenue", "sales.count"],
                    "dimensions": ["sales.product_category"],
                    "order": {"sales.total_revenue": "desc"}
                },
                description="Product category performance analysis",
                business_value="Inventory optimization, product strategy, pricing decisions",
                difficulty_level="basic"
            ),
            
            TestCase(
                name="channel_effectiveness",
                category="Sales Analytics",
                natural_language="Compare average order value across different sales channels",
                expected_query={
                    "measures": ["sales.average_order_value", "sales.count"],
                    "dimensions": ["sales.channel"],
                    "order": {"sales.average_order_value": "desc"}
                },
                description="Sales channel performance comparison",
                business_value="Channel investment decisions, sales strategy optimization",
                difficulty_level="intermediate"
            ),
            
            TestCase(
                name="discount_impact",
                category="Sales Analytics", 
                natural_language="How do discount tiers affect total sales volume?",
                expected_query={
                    "measures": ["sales.total_revenue", "sales.count", "sales.total_discount_amount"],
                    "dimensions": ["sales.discount_tier"],
                    "order": {"sales.total_revenue": "desc"}
                },
                description="Discount strategy impact analysis",
                business_value="Pricing strategy, promotion effectiveness, margin optimization",
                difficulty_level="advanced"
            ),
            
            # ===== CROSS-DOMAIN INSIGHTS =====
            TestCase(
                name="payment_preferences",
                category="Financial Analytics",
                natural_language="What payment methods are most popular and generate highest revenue?",
                expected_query={
                    "measures": ["sales.count", "sales.total_revenue", "sales.average_order_value"],
                    "dimensions": ["sales.payment_method"],
                    "order": {"sales.total_revenue": "desc"}
                },
                description="Payment method preference and performance analysis",
                business_value="Payment processing optimization, customer experience improvement",
                difficulty_level="intermediate"
            ),
            
            # ===== ADVANCED ANALYTICS =====
            TestCase(
                name="customer_credit_performance",
                category="Risk Analytics",
                natural_language="Show average customer lifetime value by credit score tier",
                expected_query={
                    "measures": ["customers.average_lifetime_value", "customers.count", "customers.average_credit_score"],
                    "dimensions": ["customers.credit_score_tier"],
                    "order": {"customers.average_lifetime_value": "desc"}
                },
                description="Credit risk vs customer value correlation",
                business_value="Credit policy optimization, risk-based pricing, customer acquisition",
                difficulty_level="advanced"
            ),
            
            # ===== OPERATIONAL INSIGHTS =====
            TestCase(
                name="product_category_trends",
                category="Product Analytics",
                natural_language="Which product categories have the highest quantity sold?", 
                expected_query={
                    "measures": ["sales.total_quantity", "sales.count"],
                    "dimensions": ["sales.product_category"],
                    "order": {"sales.total_quantity": "desc"}
                },
                description="Product volume analysis by category",
                business_value="Inventory planning, supply chain optimization, demand forecasting",
                difficulty_level="basic"
            ),
            
            TestCase(
                name="comprehensive_sales_overview",
                category="Executive Dashboard",
                natural_language="Give me a complete sales overview with revenue, orders, and average values",
                expected_query={
                    "measures": ["sales.total_revenue", "sales.count", "sales.average_order_value", "sales.total_quantity"]
                },
                description="Executive-level sales performance summary",
                business_value="Strategic decision making, board reporting, performance monitoring",
                difficulty_level="basic"
            )
        ]
    
    async def execute_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a query against the semantic layer"""
        response = await self.client.post(
            f"{self.base_url}/cubejs-api/v1/load",
            json={"query": query},
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    
    async def run_test_case(self, test_case: TestCase) -> TestResult:
        """Execute a single test case"""
        start_time = time.time()
        
        try:
            # Execute the query
            result = await self.execute_query(test_case.expected_query)
            execution_time = (time.time() - start_time) * 1000
            
            # Extract insights from the data
            insights = self.generate_insights(result.get('data', []), test_case)
            
            return TestResult(
                test_case=test_case,
                success=True,
                execution_time_ms=execution_time,
                result_data=result.get('data', []),
                insights=insights
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return TestResult(
                test_case=test_case,
                success=False,
                execution_time_ms=execution_time,
                error_message=str(e)
            )
    
    def generate_insights(self, data: List[Dict[str, Any]], test_case: TestCase) -> str:
        """Generate human-readable insights from query results"""
        if not data:
            return "No data returned from query."
        
        insights = []
        
        # Add category-specific insights
        if test_case.category == "Geographic Analysis":
            if "cities.total_population" in data[0]:
                top_city = data[0]
                population = top_city.get('cities.total_population', 'N/A')
                try:
                    pop_num = int(population) if isinstance(population, str) else population
                    insights.append(f"🏙️ {top_city.get('cities.city_name', 'N/A')} is the most populous city with {pop_num:,} residents")
                except (ValueError, TypeError):
                    insights.append(f"🏙️ {top_city.get('cities.city_name', 'N/A')} is the most populous city with {population} residents")
                
            if "cities.count" in data[0]:
                total_cities = sum(int(row.get('cities.count', 0)) for row in data)
                insights.append(f"📊 Total cities analyzed: {total_cities}")
                
        elif test_case.category == "Sales Analytics":
            if "sales.total_revenue" in data[0]:
                total_revenue = sum(float(row.get('sales.total_revenue', 0)) for row in data)
                insights.append(f"💰 Total revenue: ${total_revenue:,.2f}")
                
                if len(data) > 1:
                    top_performer = data[0]
                    category_key = next((k for k in top_performer.keys() if 'category' in k or 'channel' in k), None)
                    if category_key:
                        revenue = top_performer.get('sales.total_revenue', 0)
                        if isinstance(revenue, (int, float)):
                            insights.append(f"🥇 Top performer: {top_performer.get(category_key)} with ${revenue:,.2f}")
                        else:
                            insights.append(f"🥇 Top performer: {top_performer.get(category_key)} with ${revenue}")
        
        elif test_case.category == "Customer Analytics":
            if "customers.count" in data[0]:
                total_customers = sum(int(row.get('customers.count', 0)) for row in data)
                insights.append(f"👥 Total customers: {total_customers:,}")
                
            if "customers.average_lifetime_value" in data[0]:
                avg_ltv = sum(float(row.get('customers.average_lifetime_value', 0)) for row in data) / len(data)
                insights.append(f"💎 Average customer lifetime value: ${avg_ltv:,.2f}")
        
        # Add performance insights
        if len(data) >= 3:
            insights.append(f"📈 Analyzed {len(data)} segments/categories")
        
        return " | ".join(insights) if insights else f"✅ Successfully retrieved {len(data)} data points"
    
    async def run_demo_suite(self) -> Dict[str, Any]:
        """Run the complete demo test suite"""
        test_cases = self.get_demo_test_cases()
        results = []
        
        print("🚀 Starting DuckLake Semantic Layer Demo Test Suite")
        print("=" * 80)
        
        category_stats = {}
        total_start_time = time.time()
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] {test_case.name}")
            print(f"📝 Natural Language: '{test_case.natural_language}'")
            print(f"🎯 Category: {test_case.category} | Difficulty: {test_case.difficulty_level}")
            
            result = await self.run_test_case(test_case)
            results.append(result)
            
            if result.success:
                print(f"✅ Success ({result.execution_time_ms:.1f}ms)")
                print(f"💡 Insights: {result.insights}")
                if result.result_data:
                    print(f"📊 Data points: {len(result.result_data)}")
            else:
                print(f"❌ Failed: {result.error_message}")
            
            # Update category stats
            if test_case.category not in category_stats:
                category_stats[test_case.category] = {"total": 0, "success": 0}
            category_stats[test_case.category]["total"] += 1
            if result.success:
                category_stats[test_case.category]["success"] += 1
        
        total_time = time.time() - total_start_time
        
        # Generate summary
        successful_tests = sum(1 for r in results if r.success)
        avg_response_time = sum(r.execution_time_ms for r in results if r.success) / max(successful_tests, 1)
        
        summary = {
            "total_tests": len(test_cases),
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / len(test_cases)) * 100,
            "total_execution_time": total_time,
            "average_response_time_ms": avg_response_time,
            "category_breakdown": category_stats,
            "results": results
        }
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 DEMO TEST SUITE SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {successful_tests}/{len(test_cases)} ({summary['success_rate']:.1f}%)")
        print(f"⚡ Average Response Time: {avg_response_time:.1f}ms")
        print(f"⏱️ Total Execution Time: {total_time:.2f}s")
        
        print(f"\n📈 Performance by Category:")
        for category, stats in category_stats.items():
            success_rate = (stats["success"] / stats["total"]) * 100
            print(f"   {category}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
        
        return summary


async def main():
    """Main demo execution"""
    demo = SemanticLayerDemo()
    
    try:
        # Test connection first
        print("🔗 Testing connection to semantic layer...")
        response = await demo.client.get(f"{demo.base_url}/cubejs-api/v1/meta")
        if response.status_code == 200:
            meta = response.json()
            print(f"✅ Connected! Found {len(meta.get('cubes', []))} cubes available")
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return
        
        # Run the demo suite
        summary = await demo.run_demo_suite()
        
        # Save results for further analysis
        with open("demo_results.json", "w") as f:
            # Convert results to JSON-serializable format
            json_results = {
                **summary,
                "results": [
                    {
                        "name": r.test_case.name,
                        "category": r.test_case.category,
                        "natural_language": r.test_case.natural_language,
                        "success": r.success,
                        "execution_time_ms": r.execution_time_ms,
                        "insights": r.insights,
                        "business_value": r.test_case.business_value,
                        "difficulty": r.test_case.difficulty_level
                    }
                    for r in summary["results"]
                ]
            }
            json.dump(json_results, f, indent=2)
        
        print(f"\n📁 Detailed results saved to demo_results.json")
        print(f"🎯 Demo complete! Ready for AI agent integration.")
        
    finally:
        await demo.close()


if __name__ == "__main__":
    asyncio.run(main())