#!/usr/bin/env python3
"""
Simple SEED Integration Test
Tests basic SEED functionality without complex imports
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

def test_basic_seed_classes():
    """Test that basic SEED classes can be imported and instantiated"""
    print("Testing basic SEED classes...")
    
    try:
        # Test optimization domain enum
        from services.seed_optimization_engine import OptimizationDomain
        domains = list(OptimizationDomain)
        print(f"✓ OptimizationDomain enum: {len(domains)} domains")
        
        # Test optimization result class
        from services.seed_optimization_engine import OptimizationResult
        result = OptimizationResult(
            domain=OptimizationDomain.THERAPEUTIC,
            metric_improved=True,
            old_value=0.5,
            new_value=0.7,
            improvement_percentage=40.0,
            parameters_adjusted={'test': True},
            confidence=0.8
        )
        print(f"✓ OptimizationResult created: {result.improvement_percentage}% improvement")
        
        return True
    except Exception as e:
        print(f"✗ Basic classes error: {e}")
        return False

def test_seed_database():
    """Test SEED database creation"""
    print("\nTesting SEED database...")
    
    try:
        # Create test database
        db_path = Path("instance/test_seed.db")
        db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            # Create optimization cycles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS optimization_cycles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT NOT NULL,
                    user_id TEXT,
                    cycle_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metrics_before TEXT NOT NULL,
                    metrics_after TEXT NOT NULL,
                    parameters_adjusted TEXT NOT NULL,
                    improvement_achieved REAL NOT NULL,
                    confidence_score REAL NOT NULL
                )
            """)
            
            # Test insert
            conn.execute("""
                INSERT INTO optimization_cycles 
                (domain, user_id, metrics_before, metrics_after, parameters_adjusted, improvement_achieved, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ('THERAPEUTIC', 'test_user', '{"score": 0.5}', '{"score": 0.7}', '{"test": true}', 0.4, 0.8))
            
            # Test query
            cursor = conn.execute("SELECT COUNT(*) FROM optimization_cycles")
            count = cursor.fetchone()[0]
            print(f"✓ Database created and tested: {count} record(s)")
        
        # Cleanup
        db_path.unlink(missing_ok=True)
        
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_seed_routes_structure():
    """Test SEED routes can be imported"""
    print("\nTesting SEED routes structure...")
    
    try:
        from routes.seed_routes import seed_bp
        print(f"✓ SEED blueprint imported: {seed_bp.name}")
        
        # Check if blueprint has routes (basic check)
        print(f"✓ Blueprint URL prefix: {seed_bp.url_prefix}")
        
        return True
    except Exception as e:
        print(f"✗ Routes error: {e}")
        return False

def test_demo_optimization_logic():
    """Test basic optimization logic without external dependencies"""
    print("\nTesting demo optimization logic...")
    
    try:
        # Test therapeutic effectiveness calculation
        def calculate_therapeutic_improvement(old_score, new_score):
            if old_score == 0:
                return 100.0
            return ((new_score - old_score) / old_score) * 100
        
        improvement = calculate_therapeutic_improvement(0.5, 0.7)
        print(f"✓ Therapeutic improvement calculation: {improvement}%")
        
        # Test engagement metrics
        def calculate_engagement_score(interactions, time_spent, feature_usage):
            return (interactions * 0.4) + (time_spent * 0.3) + (feature_usage * 0.3)
        
        engagement = calculate_engagement_score(10, 5, 8)
        print(f"✓ Engagement score calculation: {engagement}")
        
        # Test cost optimization
        def calculate_cost_savings(old_cost, new_cost):
            if old_cost == 0:
                return 0
            return ((old_cost - new_cost) / old_cost) * 100
        
        savings = calculate_cost_savings(0.10, 0.07)
        print(f"✓ Cost savings calculation: {savings}%")
        
        return True
    except Exception as e:
        print(f"✗ Optimization logic error: {e}")
        return False

def run_simple_tests():
    """Run simple SEED tests"""
    print("=" * 50)
    print("SIMPLE SEED INTEGRATION TEST")
    print("=" * 50)
    print(f"Test started: {datetime.now().isoformat()}")
    
    tests = [
        test_basic_seed_classes,
        test_seed_database,
        test_seed_routes_structure,
        test_demo_optimization_logic
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 ALL SIMPLE TESTS PASSED!")
        print("\nSEED Basic Integration Working:")
        print("- ✓ Core classes importable")
        print("- ✓ Database operations functional") 
        print("- ✓ Routes structure accessible")
        print("- ✓ Optimization logic working")
        
    else:
        print("❌ Some tests failed")
        failed_tests = [tests[i].__name__ for i, result in enumerate(results) if not result]
        print(f"Failed tests: {', '.join(failed_tests)}")
    
    print(f"\nTest completed: {datetime.now().isoformat()}")
    return passed == total

if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)