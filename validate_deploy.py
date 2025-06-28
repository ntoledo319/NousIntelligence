#!/usr/bin/env python3
"""Quick deployment validation"""
import requests
import sys

def test_public_access(base_url="http://0.0.0.0:8080"):
    """Test public access works"""
    try:
        # Test landing page
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Landing page accessible")
        else:
            print(f"❌ Landing page error: {response.status_code}")
            return False
        
        # Test demo page
        response = requests.get(f"{base_url}/demo", timeout=5)
        if response.status_code == 200:
            print("✅ Demo page accessible")
        else:
            print(f"❌ Demo page error: {response.status_code}")
        
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint error: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    if test_public_access():
        print("🎉 Deployment validation PASSED")
        sys.exit(0)
    else:
        print("💥 Deployment validation FAILED")
        sys.exit(1)
