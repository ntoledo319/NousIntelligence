"""
Comprehensive Test Execution Script
Runs all testing infrastructure with proper coordination and reporting
"""
import os
import sys
import subprocess
import time
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

def run_master_test_suite():
    """Run the complete master test suite"""
    print("🚀 Starting Comprehensive Test Infrastructure")
    print("=" * 60)
    print("Testing Framework: Zero Authentication Barriers")
    print("Scope: Complete bug detection and problem resolution")
    print("=" * 60)
    
    try:
        # Run master test orchestrator
        from master_test_orchestrator import MasterTestOrchestrator
        
        orchestrator = MasterTestOrchestrator()
        results = orchestrator.run_complete_testing_suite()
        
        print("\n" + "=" * 60)
        print("TEST EXECUTION COMPLETE")
        print("=" * 60)
        
        # Display summary
        summary = results['test_summary']
        deployment = results['deployment_readiness']
        
        print(f"Overall Score: {summary['overall_score']:.1f}/100")
        print(f"Deployment Status: {deployment['readiness']}")
        print(f"Total Time: {summary['total_time']:.2f}s")
        
        print("\nCategory Scores:")
        for category, score in summary['scores'].items():
            status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            print(f"  {status} {category.title()}: {score:.1f}/100")
        
        print("\nKey Findings:")
        
        # Authentication status
        auth_results = results['detailed_results'].get('authentication_barriers', {})
        remaining_barriers = auth_results.get('remaining_barriers', 0)
        if remaining_barriers == 0:
            print("  ✅ No authentication barriers detected")
        else:
            print(f"  ❌ {remaining_barriers} authentication barriers remain")
        
        # Error status
        error_results = results['detailed_results'].get('error_detection', {})
        if 'summary' in error_results:
            total_errors = error_results['summary'].get('total_errors', 0)
            critical_errors = error_results['summary'].get('critical_errors', 0)
            if total_errors == 0:
                print("  ✅ No errors detected")
            else:
                print(f"  ⚠️ {total_errors} errors found ({critical_errors} critical)")
        
        # Performance status
        perf_results = results['detailed_results'].get('performance_metrics', {})
        if 'response_times' in perf_results:
            slow_endpoints = sum(1 for data in perf_results['response_times'].values() 
                               if isinstance(data, dict) and data.get('time', 0) > 1.0)
            if slow_endpoints == 0:
                print("  ✅ All endpoints respond quickly")
            else:
                print(f"  ⚠️ {slow_endpoints} slow endpoints detected")
        
        # Recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            print(f"\nRecommendations ({len(recommendations)}):")
            for rec in recommendations[:3]:  # Show top 3
                print(f"  {rec['priority']}: {rec['issue']}")
            if len(recommendations) > 3:
                print(f"  ... and {len(recommendations) - 3} more")
        else:
            print("\n✅ No critical issues found!")
        
        print(f"\nDetailed reports available in:")
        print(f"  - tests/master_test_report.md")
        print(f"  - tests/master_test_report.json")
        print(f"  - tests/authentication_barrier_report.md")
        print(f"  - tests/advanced_error_report.md")
        print(f"  - tests/comprehensive_test_report.md")
        
        # Return appropriate exit code
        if deployment['readiness'] in ['READY', 'MOSTLY_READY']:
            print("\n🎉 System ready for deployment!")
            return 0
        else:
            print(f"\n⚠️ System needs work before deployment")
            return 1
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        print(f"\n❌ Test execution failed: {e}")
        return 1

def run_individual_test_suites():
    """Run individual test suites for debugging"""
    print("\n🔧 Running Individual Test Suites for Debugging")
    print("-" * 40)
    
    test_suites = [
        ("Authentication Barrier Detection", "authentication_barrier_detector.py"),
        ("Advanced Error Detection", "advanced_error_testing.py"),
        ("Comprehensive Test Suite", "comprehensive_test_suite.py")
    ]
    
    results = {}
    
    for suite_name, script_name in test_suites:
        print(f"\n🔍 Running {suite_name}...")
        try:
            script_path = Path(__file__).parent / script_name
            if script_path.exists():
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    print(f"  ✅ {suite_name} completed successfully")
                    results[suite_name] = "success"
                else:
                    print(f"  ❌ {suite_name} failed (exit code: {result.returncode})")
                    if result.stderr:
                        print(f"     Error: {result.stderr[:200]}...")
                    results[suite_name] = "failed"
                    
            else:
                print(f"  ⚠️ {suite_name} script not found: {script_name}")
                results[suite_name] = "not_found"
                
        except subprocess.TimeoutExpired:
            print(f"  ⏰ {suite_name} timed out")
            results[suite_name] = "timeout"
        except Exception as e:
            print(f"  ❌ {suite_name} error: {e}")
            results[suite_name] = "error"
    
    print(f"\n📊 Individual Test Results:")
    for suite_name, status in results.items():
        status_icon = {
            "success": "✅",
            "failed": "❌", 
            "not_found": "❓",
            "timeout": "⏰",
            "error": "💥"
        }.get(status, "❓")
        print(f"  {status_icon} {suite_name}: {status}")
    
    return results

def check_test_environment():
    """Check if test environment is properly set up"""
    print("🔍 Checking Test Environment")
    print("-" * 30)
    
    checks = []
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"  ✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        checks.append(True)
    else:
        print(f"  ❌ Python version too old: {python_version.major}.{python_version.minor}.{python_version.micro}")
        checks.append(False)
    
    # Check critical files
    critical_files = [
        'app.py',
        'config.py', 
        'database.py',
        'utils/auth_compat.py',
        'tests/master_test_orchestrator.py',
        'tests/authentication_barrier_detector.py',
        'tests/advanced_error_testing.py',
        'tests/comprehensive_test_suite.py'
    ]
    
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
            checks.append(True)
        else:
            print(f"  ❌ Missing: {file_path}")
            checks.append(False)
    
    # Check Python modules
    required_modules = [
        'flask',
        'requests', 
        'psutil',
        'pathlib'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ Module: {module}")
            checks.append(True)
        except ImportError:
            print(f"  ❌ Missing module: {module}")
            checks.append(False)
    
    success_rate = sum(checks) / len(checks)
    
    if success_rate >= 0.9:
        print(f"\n✅ Environment check passed ({success_rate:.1%})")
        return True
    else:
        print(f"\n❌ Environment check failed ({success_rate:.1%})")
        return False

def main():
    """Main entry point"""
    print("🧪 NOUS Testing Infrastructure")
    print("Comprehensive Bug Detection and Authentication Barrier Elimination")
    print("=" * 70)
    
    # Check environment first
    if not check_test_environment():
        print("❌ Environment check failed. Please fix issues and try again.")
        return 1
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run NOUS testing infrastructure")
    parser.add_argument('--mode', choices=['master', 'individual', 'both'], 
                       default='master', help='Testing mode')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        print("🐛 Debug mode enabled")
    
    start_time = time.time()
    
    try:
        if args.mode in ['master', 'both']:
            print("\n" + "=" * 70)
            print("RUNNING MASTER TEST SUITE")
            print("=" * 70)
            master_result = run_master_test_suite()
        else:
            master_result = 0
        
        if args.mode in ['individual', 'both']:
            print("\n" + "=" * 70) 
            print("RUNNING INDIVIDUAL TEST SUITES")
            print("=" * 70)
            individual_results = run_individual_test_suites()
            
            # Convert individual results to exit code
            failed_tests = sum(1 for status in individual_results.values() 
                             if status in ['failed', 'error', 'timeout'])
            individual_result = 1 if failed_tests > 0 else 0
        else:
            individual_result = 0
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "=" * 70)
        print("TESTING COMPLETE")
        print("=" * 70)
        print(f"Total execution time: {total_time:.2f} seconds")
        
        # Determine final result
        final_result = max(master_result, individual_result) if args.mode == 'both' else master_result or individual_result
        
        if final_result == 0:
            print("🎉 All tests completed successfully!")
            print("✅ System appears ready for deployment")
        else:
            print("⚠️ Some tests failed or found issues")
            print("📋 Please review test reports and address identified problems")
        
        return final_result
        
    except KeyboardInterrupt:
        print("\n⏹️ Testing interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())