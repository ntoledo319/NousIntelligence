#!/usr/bin/env python3
"""
Comprehensive Test Runner
Runs all generated tests and provides coverage report
"""

import os
import sys
import subprocess
from pathlib import Path

def run_all_tests():
    """Run all generated tests"""
    print("🧪 Running Comprehensive Test Suite")
    print("=" * 50)
    
    test_files = [
        'tests/test_generated_api.py',
        'tests/test_generated_functions.py', 
        'tests/test_generated_models.py',
        'tests/test_generated_integration.py'
    ]
    
    results = {}
    
    for test_file in test_files:
        if Path(test_file).exists():
            print(f"\n🔍 Running {test_file}")
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pytest', test_file, '-v'
                ], capture_output=True, text=True, timeout=60)
                
                results[test_file] = {
                    'returncode': result.returncode,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
                if result.returncode == 0:
                    print(f"✅ {test_file} PASSED")
                else:
                    print(f"❌ {test_file} FAILED")
                    if result.stderr:
                        print(f"Error: {result.stderr[:200]}")
                        
            except subprocess.TimeoutExpired:
                print(f"⏰ {test_file} TIMEOUT")
                results[test_file] = {'returncode': -1, 'error': 'timeout'}
            except Exception as e:
                print(f"💥 {test_file} ERROR: {e}")
                results[test_file] = {'returncode': -1, 'error': str(e)}
    
    # Generate summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    passed = sum(1 for r in results.values() if r.get('returncode') == 0)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Coverage: {(passed/total)*100:.1f}%")
    
    return results

if __name__ == "__main__":
    run_all_tests()
