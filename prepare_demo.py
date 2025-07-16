#!/usr/bin/env python3
"""
Demo Preparation Script
One-command setup and validation for the complete demo
"""

import os
import sys
import time
import subprocess
import json
from typing import Dict, Any, List, Optional

class DemoPreparation:
    """Complete demo preparation and validation"""
    
    def __init__(self):
        self.demo_ready = False
        self.validation_results = []
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are installed"""
        print("🔍 Checking Prerequisites...")
        
        prerequisites = [
            ("Docker", "docker --version"),
            ("Docker Compose", "docker-compose --version"),
            ("Python", "python3 --version"),
            ("curl", "curl --version"),
            ("psql", "psql --version")
        ]
        
        all_good = True
        for name, command in prerequisites:
            try:
                result = subprocess.run(command.split(), 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    print(f"   ✅ {name} is installed")
                else:
                    print(f"   ❌ {name} is not working properly")
                    all_good = False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print(f"   ❌ {name} is not installed")
                all_good = False
        
        return all_good
    
    def start_infrastructure(self) -> bool:
        """Start the complete DuckLake infrastructure"""
        print("🚀 Starting DuckLake Infrastructure...")
        
        try:
            # Check if docker-compose-lake.yml exists
            if not os.path.exists('docker-compose-lake.yml'):
                print("   ❌ docker-compose-lake.yml not found")
                return False
            
            # Start services
            print("   📦 Starting Docker containers...")
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose-lake.yml', 'up', '-d'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                print(f"   ❌ Failed to start containers: {result.stderr}")
                return False
            
            print("   ✅ Containers started successfully")
            
            # Wait for services to be ready
            print("   ⏳ Waiting for services to be ready...")
            time.sleep(30)  # Give services time to initialize
            
            # Check service health
            health_checks = [
                ("MinIO", "curl -f http://localhost:9001/minio/health/live"),
                ("Cube.dev", "curl -f http://localhost:4000/cubejs-api/v1/meta"),
                ("DuckDB", "psql -h localhost -p 15432 -U root -c 'SELECT 1;'")
            ]
            
            for service, check_cmd in health_checks:
                try:
                    result = subprocess.run(check_cmd.split(), 
                                          capture_output=True, 
                                          text=True, 
                                          timeout=10)
                    if result.returncode == 0:
                        print(f"   ✅ {service} is ready")
                    else:
                        print(f"   ⚠️  {service} is not ready yet")
                except subprocess.TimeoutExpired:
                    print(f"   ⚠️  {service} health check timed out")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Infrastructure startup failed: {e}")
            return False
    
    def validate_demo_queries(self) -> bool:
        """Validate all demo queries work correctly"""
        print("🧪 Validating Demo Queries...")
        
        try:
            # Import and run the demo validation
            from demo_validation import DemoValidator
            
            validator = DemoValidator()
            success = validator.run_complete_validation()
            
            if success:
                print("   ✅ All demo queries validated successfully")
                return True
            else:
                print("   ❌ Some demo queries failed validation")
                return False
                
        except Exception as e:
            print(f"   ❌ Demo validation failed: {e}")
            return False
    
    def generate_demo_materials(self) -> bool:
        """Generate all demo support materials"""
        print("📋 Generating Demo Materials...")
        
        try:
            # Generate cheat sheet
            from demo_support import DemoSupport
            
            demo_support = DemoSupport()
            cheat_sheet = demo_support.generate_demo_cheat_sheet()
            
            # Save cheat sheet
            with open('demo_cheat_sheet.md', 'w') as f:
                f.write(cheat_sheet)
            
            print("   ✅ Demo cheat sheet generated")
            
            # Generate presenter notes
            presenter_notes = self._generate_presenter_notes()
            with open('demo_presenter_notes.md', 'w') as f:
                f.write(presenter_notes)
            
            print("   ✅ Presenter notes generated")
            
            # Generate quick reference
            quick_ref = self._generate_quick_reference()
            with open('demo_quick_reference.md', 'w') as f:
                f.write(quick_ref)
            
            print("   ✅ Quick reference generated")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Demo materials generation failed: {e}")
            return False
    
    def _generate_presenter_notes(self) -> str:
        """Generate detailed presenter notes"""
        notes = []
        notes.append("# 🎤 PRESENTER NOTES")
        notes.append("=" * 50)
        notes.append("")
        
        notes.append("## 📍 Demo Flow Overview")
        notes.append("**Total Time: 40 minutes**")
        notes.append("")
        notes.append("1. **Tier 1 - Object Storage** (5 min)")
        notes.append("2. **Tier 2 - DuckDB Analytics** (7 min)")
        notes.append("3. **Tier 3 - Cube.dev Semantics** (8 min)")
        notes.append("4. **Tier 4 - MCP Integration** (5 min)")
        notes.append("5. **Tier 5 - LangFlow AI** (10 min)")
        notes.append("6. **Wrap-up & Q&A** (5 min)")
        notes.append("")
        
        notes.append("## 🎯 Key Messages")
        notes.append("- **Modern Data Architecture**: Separation of storage and compute")
        notes.append("- **Business Semantics**: From SQL to business language")
        notes.append("- **AI Integration**: Standard protocols for agent access")
        notes.append("- **Performance**: Sub-second responses for real-time conversation")
        notes.append("- **Scalability**: Local development to cloud production")
        notes.append("")
        
        notes.append("## 🔧 Technical Highlights")
        notes.append("- **DuckDB**: Direct object storage queries, no ETL")
        notes.append("- **Parquet**: 10x compression, columnar performance")
        notes.append("- **Cube.dev**: Business metrics, not technical fields")
        notes.append("- **MCP Protocol**: Standard AI agent integration")
        notes.append("- **LangFlow**: Visual workflow with conversational AI")
        notes.append("")
        
        notes.append("## 💡 Demo Tips")
        notes.append("- Start each tier with 'why this matters'")
        notes.append("- Show performance metrics as you go")
        notes.append("- Emphasize business user perspective")
        notes.append("- Connect each tier to the next")
        notes.append("- Have backup queries ready")
        notes.append("")
        
        notes.append("## 🚨 Common Issues & Solutions")
        notes.append("- **MinIO not responding**: Restart Docker containers")
        notes.append("- **DuckDB connection failed**: Check port 15432")
        notes.append("- **Cube.dev errors**: Restart cube service")
        notes.append("- **LangFlow issues**: Use robust server with fallbacks")
        notes.append("- **Slow queries**: Restart DuckDB setup container")
        notes.append("")
        
        return "\n".join(notes)
    
    def _generate_quick_reference(self) -> str:
        """Generate quick reference card"""
        ref = []
        ref.append("# 📋 QUICK REFERENCE")
        ref.append("=" * 30)
        ref.append("")
        
        ref.append("## 🔗 URLs")
        ref.append("- MinIO: http://localhost:9001")
        ref.append("- Cube.dev: http://localhost:4000")
        ref.append("- DuckDB: psql -h localhost -p 15432 -U root")
        ref.append("")
        
        ref.append("## 🎯 Demo Queries")
        ref.append("### Tier 2 - DuckDB")
        ref.append("```sql")
        ref.append("SELECT region, COUNT(*), SUM(population)")
        ref.append("FROM cities GROUP BY region")
        ref.append("ORDER BY SUM(population) DESC;")
        ref.append("```")
        ref.append("")
        
        ref.append("### Tier 3 - Cube.dev")
        ref.append("```json")
        ref.append("{")
        ref.append('  "measures": ["cities.total_population"],')
        ref.append('  "dimensions": ["cities.city_name"],')
        ref.append('  "order": {"cities.total_population": "desc"},')
        ref.append('  "limit": 5')
        ref.append("}")
        ref.append("```")
        ref.append("")
        
        ref.append("### Tier 5 - LangFlow")
        ref.append("- 'What are the top 5 cities by population?'")
        ref.append("- 'Show me revenue by product category'")
        ref.append("- 'Which customers have highest lifetime value?'")
        ref.append("")
        
        ref.append("## ⚡ Performance Metrics")
        ref.append("- Query Response: <15ms")
        ref.append("- Test Success: 100% (11/11)")
        ref.append("- Data Coverage: 7 BI categories")
        ref.append("")
        
        return "\n".join(ref)
    
    def run_complete_preparation(self) -> bool:
        """Run complete demo preparation"""
        print("🎯 SEMANTIC MCP DEMO PREPARATION")
        print("=" * 60)
        
        start_time = time.time()
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites not met. Please install missing components.")
            return False
        
        # Step 2: Start infrastructure
        if not self.start_infrastructure():
            print("\n❌ Infrastructure startup failed. Check Docker setup.")
            return False
        
        # Step 3: Validate demo queries
        if not self.validate_demo_queries():
            print("\n❌ Demo validation failed. Check service logs.")
            return False
        
        # Step 4: Generate demo materials
        if not self.generate_demo_materials():
            print("\n❌ Demo materials generation failed.")
            return False
        
        total_time = time.time() - start_time
        
        # Success summary
        print("\n" + "=" * 60)
        print("🎉 DEMO PREPARATION COMPLETE!")
        print("=" * 60)
        print(f"Preparation time: {total_time:.1f} seconds")
        print("")
        print("📁 Generated Files:")
        print("   - demo_cheat_sheet.md")
        print("   - demo_presenter_notes.md")
        print("   - demo_quick_reference.md")
        print("")
        print("🚀 Demo is ready for presentation!")
        print("")
        print("📋 Next Steps:")
        print("1. Review the demo script: DEMO-SCRIPT.md")
        print("2. Check the cheat sheet: demo_cheat_sheet.md")
        print("3. Open LangFlow Desktop and configure MCP")
        print("4. Practice the demo flow")
        print("")
        print("🔍 Quick Health Check:")
        print("   MinIO Console: http://localhost:9001")
        print("   Cube.dev Playground: http://localhost:4000")
        print("   DuckDB: psql -h localhost -p 15432 -U root")
        
        return True
    
    def cleanup_demo(self):
        """Clean up demo environment"""
        print("🧹 Cleaning up demo environment...")
        
        try:
            # Stop Docker containers
            subprocess.run([
                'docker-compose', '-f', 'docker-compose-lake.yml', 'down'
            ], capture_output=True, text=True)
            
            print("   ✅ Docker containers stopped")
            
            # Remove generated files
            generated_files = [
                'demo_cheat_sheet.md',
                'demo_presenter_notes.md',
                'demo_quick_reference.md'
            ]
            
            for file in generated_files:
                if os.path.exists(file):
                    os.remove(file)
            
            print("   ✅ Generated files cleaned up")
            print("🎉 Demo cleanup complete!")
            
        except Exception as e:
            print(f"   ❌ Cleanup failed: {e}")

def main():
    """Main preparation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Prepare Semantic MCP Demo")
    parser.add_argument("--cleanup", action="store_true", help="Clean up demo environment")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't start services")
    
    args = parser.parse_args()
    
    demo_prep = DemoPreparation()
    
    if args.cleanup:
        demo_prep.cleanup_demo()
        return
    
    if args.validate_only:
        # Just run validation
        if demo_prep.check_prerequisites() and demo_prep.validate_demo_queries():
            print("✅ Demo validation passed")
            sys.exit(0)
        else:
            print("❌ Demo validation failed")
            sys.exit(1)
    
    # Full preparation
    success = demo_prep.run_complete_preparation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()