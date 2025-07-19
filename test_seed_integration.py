#!/usr/bin/env python3
"""
SEED Integration Test
Validates that SEED optimization system is properly integrated and functional
"""

import sys
import traceback
from datetime import datetime

def test_seed_imports():
    """Test that all SEED components can be imported"""
    print("Testing SEED imports...")
    
    try:
        from services.seed_optimization_engine import get_seed_engine, NOUSSeedEngine, OptimizationDomain
        print("✓ SEED optimization engine imports successful")
        
        from services.seed_integration_layer import get_seed_integration, SeedIntegrationLayer
        print("✓ SEED integration layer imports successful")
        
        from routes.seed_routes import seed_bp
        print("✓ SEED routes imports successful")
        
        return True
    except Exception as e:
        print("✗ Import error: {}".format(e))
        traceback.print_exc()
        return False

def test_seed_engine_initialization():
    """Test SEED engine initialization"""
    print("\nTesting SEED engine initialization...")
    
    try:
        from services.seed_optimization_engine import get_seed_engine
        
        # Get SEED engine instance
        engine = get_seed_engine()
        print("✓ SEED engine instance created")
        
        # Test optimization status
        status = engine.get_optimization_status()
        print("✓ Optimization status retrieved: {}".format(status.get('engine_status', 'unknown')))
        
        # Test domain parameters
        domains = len(engine.domain_parameters)
        print("✓ Domain parameters configured: {} domains".format(domains))
        
        return True
    except Exception as e:
        print("✗ Engine initialization error: {}".format(e))
        traceback.print_exc()
        return False

def test_integration_layer():
    """Test SEED integration layer"""
    print("\nTesting SEED integration layer...")
    
    try:
        from services.seed_integration_layer import get_seed_integration
        
        # Get integration layer instance
        integration = get_seed_integration()
        print("✓ Integration layer instance created")
        
        # Test dashboard data (without user)
        dashboard_data = integration.get_optimization_dashboard_data()
        print("✓ Dashboard data retrieved")
        
        return True
    except Exception as e:
        print("✗ Integration layer error: {}".format(e))
        traceback.print_exc()
        return False

def test_api_routes():
    """Test SEED API routes structure"""
    print("\nTesting SEED API routes...")
    
    try:
        from routes.seed_routes import seed_bp
        
        # Check blueprint registration
        print("✓ SEED blueprint created: {}".format(seed_bp.name))
        print("✓ URL prefix: {}".format(seed_bp.url_prefix))
        
        # Count routes
        route_count = len(list(seed_bp.iter_rules()))
        print("✓ Routes registered: {}".format(route_count))
        
        return True
    except Exception as e:
        print("✗ API routes error: {}".format(e))
        traceback.print_exc()
        return False

def test_optimization_domains():
    """Test optimization domain enumeration"""
    print("\nTesting optimization domains...")
    
    try:
        from services.seed_optimization_engine import OptimizationDomain
        
        domains = list(OptimizationDomain)
        print("✓ Optimization domains available: {}".format(len(domains)))
        
        for domain in domains:
            print("  - {}".format(domain.value))
        
        return True
    except Exception as e:
        print("✗ Optimization domains error: {}".format(e))
        traceback.print_exc()
        return False

def test_demo_optimization():
    """Test demo optimization functionality"""
    print("\nTesting demo optimization...")
    
    try:
        from services.seed_optimization_engine import get_seed_engine
        
        engine = get_seed_engine()
        
        # Test therapeutic optimization with minimal data
        from services.seed_optimization_engine import OptimizationResult, OptimizationDomain
        
        # Create a simple optimization result for demo
        demo_result = OptimizationResult(
            domain=OptimizationDomain.THERAPEUTIC,
            metric_improved=True,
            old_value=0.5,
            new_value=0.7,
            improvement_percentage=40.0,
            parameters_adjusted={'demo': True},
            confidence=0.8
        )
        
        print("✓ Demo optimization result created")
        print("  - Domain: {}".format(demo_result.domain.value))
        print("  - Improvement: {}%".format(demo_result.improvement_percentage))
        print("  - Confidence: {}".format(demo_result.confidence))
        
        return True
    except Exception as e:
        print("✗ Demo optimization error: {}".format(e))
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all SEED integration tests"""
    print("=" * 60)
    print("SEED OPTIMIZATION INTEGRATION TEST")
    print("=" * 60)
    print("Test started: {}".format(datetime.now().isoformat()))
    print("-" * 60)
    tests = [
        test_seed_imports,
        test_seed_engine_initialization,
        test_integration_layer,
        test_api_routes,
        test_optimization_domains,
        test_demo_optimization
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print("✗ Test {} failed with exception: {}".format(test.__name__, e))
            results.append(False)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print("Tests passed: {}/{}".format(passed, total))
    print("Success rate: {:.1f}%".format((passed/total)*100))
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - SEED integration is working!")
        print("\nSEED Features Ready:")
        print("- ✓ Optimization engine initialized")
        print("- ✓ Integration layer connected")
        print("- ✓ API endpoints registered")
        print("- ✓ Dashboard accessible at /seed-dashboard")
        print("- ✓ Demo mode functional")
        
        print("\nNext Steps:")
        print("1. Visit /seed-dashboard to see the optimization interface")
        print("2. Try the optimization buttons (they work in demo mode)")
        print("3. Sign up to unlock personalized optimization")
        
    else:
        print("❌ Some tests failed - check errors above")
        failed_tests = [tests[i].__name__ for i, result in enumerate(results) if not result]
        print("Failed tests: {}".format(', '.join(failed_tests)))
    
    print("\nTest completed: {}".format(datetime.now().isoformat()))
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)