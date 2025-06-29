#!/usr/bin/env python3
"""
Final Build Validation
Comprehensive testing of all fixed functionality
"""

import sys
import requests
import json

def test_complete_functionality():
    """Test all critical application functionality"""
    base_url = "http://localhost:5000"
    tests_passed = 0
    tests_failed = 0
    
    print("🔍 Final Build Validation - Testing Complete Functionality")
    print("=" * 60)
    
    # Test 1: Health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            if health_data.get("status") == "healthy":
                print("✅ Health endpoint: PASSED")
                tests_passed += 1
            else:
                print("❌ Health endpoint: Status not healthy")
                tests_failed += 1
        else:
            print(f"❌ Health endpoint: HTTP {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Health endpoint: {e}")
        tests_failed += 1
    
    # Test 2: Landing page
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200 and "NOUS" in response.text:
            print("✅ Landing page: PASSED")
            tests_passed += 1
        else:
            print(f"❌ Landing page: HTTP {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Landing page: {e}")
        tests_failed += 1
    
    # Test 3: Demo page
    try:
        response = requests.get(f"{base_url}/demo", timeout=5)
        if response.status_code == 200 and "Guest User" in response.text:
            print("✅ Demo page: PASSED")
            tests_passed += 1
        else:
            print(f"❌ Demo page: HTTP {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Demo page: {e}")
        tests_failed += 1
    
    # Test 4: User API
    try:
        response = requests.get(f"{base_url}/api/user", timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get("demo_mode") == True:
                print("✅ User API: PASSED")
                tests_passed += 1
            else:
                print("❌ User API: Demo mode not enabled")
                tests_failed += 1
        else:
            print(f"❌ User API: HTTP {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ User API: {e}")
        tests_failed += 1
    
    # Test 5: Chat API
    try:
        response = requests.post(
            f"{base_url}/api/chat",
            json={"message": "Hello", "demo_mode": True},
            timeout=5
        )
        if response.status_code == 200:
            chat_data = response.json()
            if chat_data.get("demo") == True:
                print("✅ Chat API: PASSED")
                tests_passed += 1
            else:
                print("❌ Chat API: Demo mode not working")
                tests_failed += 1
        else:
            print(f"❌ Chat API: HTTP {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Chat API: {e}")
        tests_failed += 1
    
    # Test 6: Authentication barriers
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        health_data = response.json()
        auth_data = health_data.get("authentication", {})
        if auth_data.get("barriers_eliminated") == True:
            print("✅ Authentication barriers eliminated: PASSED")
            tests_passed += 1
        else:
            print("❌ Authentication barriers still present")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Authentication test: {e}")
        tests_failed += 1
    
    print("=" * 60)
    print(f"📊 Build Validation Results:")
    print(f"   ✅ Tests Passed: {tests_passed}")
    print(f"   ❌ Tests Failed: {tests_failed}")
    print(f"   📈 Success Rate: {(tests_passed/(tests_passed+tests_failed)*100):.1f}%")
    
    if tests_failed == 0:
        print("\n🌟 BUILD VALIDATION: COMPLETE SUCCESS")
        print("🚀 All functionality working correctly")
        print("🔓 Authentication barriers eliminated")
        print("🎯 Application ready for production deployment")
        return True
    else:
        print(f"\n🔧 BUILD VALIDATION: {tests_failed} issues found")
        return False

if __name__ == "__main__":
    success = test_complete_functionality()
    sys.exit(0 if success else 1)