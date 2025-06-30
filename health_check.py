#!/usr/bin/env python3
"""
NOUS Health Check Script - Verify Application Functionality
"""
import requests
import json
import time
import sys

def check_endpoint(url, expected_status=200, timeout=5):
    """Check if an endpoint responds correctly"""
    try:
        response = requests.get(url, timeout=timeout)
        return {
            'url': url,
            'status_code': response.status_code,
            'success': response.status_code == expected_status,
            'response_time': response.elapsed.total_seconds(),
            'content_length': len(response.content)
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'success': False,
            'error': str(e),
            'response_time': timeout
        }

def check_api_endpoint(url, data=None, timeout=5):
    """Check API endpoint with POST data"""
    try:
        response = requests.post(url, json=data, timeout=timeout)
        return {
            'url': url,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'response_time': response.elapsed.total_seconds(),
            'has_json': 'application/json' in response.headers.get('content-type', ''),
            'content_length': len(response.content)
        }
    except requests.exceptions.RequestException as e:
        return {
            'url': url,
            'success': False,
            'error': str(e),
            'response_time': timeout
        }

def main():
    """Run comprehensive health check"""
    print("🏥 NOUS Health Check - Verifying Application Status")
    print("=" * 55)
    
    base_url = "http://localhost:5000"
    
    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(3)
    
    # Check core endpoints
    endpoints = [
        '/health',
        '/healthz',
        '/',
        '/demo'
    ]
    
    print("\n📋 Checking Core Endpoints:")
    print("-" * 30)
    
    all_passed = True
    for endpoint in endpoints:
        result = check_endpoint(f"{base_url}{endpoint}")
        if result['success']:
            print(f"✅ {endpoint}: OK ({result['response_time']:.3f}s)")
        else:
            print(f"❌ {endpoint}: FAILED - {result.get('error', 'Unknown error')}")
            all_passed = False
    
    # Check API endpoints
    api_endpoints = [
        ('/api/demo/chat', {'message': 'Hello, health check!'}),
        ('/api/user', None),
    ]
    
    print("\n🔌 Checking API Endpoints:")
    print("-" * 30)
    
    for endpoint, data in api_endpoints:
        if data:
            result = check_api_endpoint(f"{base_url}{endpoint}", data)
        else:
            result = check_endpoint(f"{base_url}{endpoint}")
        
        if result['success']:
            print(f"✅ {endpoint}: OK ({result['response_time']:.3f}s)")
        else:
            print(f"❌ {endpoint}: FAILED - {result.get('error', 'Unknown error')}")
            all_passed = False
    
    # Overall status
    print("\n📊 Health Check Summary:")
    print("-" * 30)
    
    if all_passed:
        print("🎉 All health checks passed - Application is healthy!")
        return 0
    else:
        print("⚠️  Some health checks failed - Review issues above")
        return 1

if __name__ == "__main__":
    sys.exit(main())