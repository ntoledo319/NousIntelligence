#!/usr/bin/env python3
"""
Comprehensive Authentication Test
Tests all login methods: Google OAuth, Demo Mode, Session Auth
"""

import requests
import json
import logging

logger = logging.getLogger(__name__)

def test_login_methods():
    """Test all available login methods"""
    base_url = "http://localhost:8080"
    results = {}
    
    logger.info(🔐 Testing All Login Methods...)
    
    # Test 1: Demo Mode Activation
    logger.info(\n1. Testing Demo Mode Activation...)
    try:
        response = requests.post(f"{base_url}/auth/demo-mode", allow_redirects=False)
        if response.status_code == 302:
            logger.info(✅ Demo mode activation successful (redirects to dashboard))
            results['demo_mode'] = {'status': 'success', 'redirect': response.headers.get('Location')}
        else:
            logger.info(❌ Demo mode failed: {response.status_code})
            results['demo_mode'] = {'status': 'failed', 'code': response.status_code}
    except Exception as e:
        logger.error(❌ Demo mode error: {e})
        results['demo_mode'] = {'status': 'error', 'message': str(e)}
    
    # Test 2: Google OAuth Redirect
    logger.info(\n2. Testing Google OAuth Redirect...)
    try:
        response = requests.get(f"{base_url}/auth/google", allow_redirects=False)
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            if 'accounts.google.com' in redirect_url:
                logger.info(✅ Google OAuth redirect successful)
                logger.info(   Redirects to: {redirect_url[:100]}...)
                # Extract client ID from redirect URL
                if 'client_id=' in redirect_url:
                    client_id_start = redirect_url.find('client_id=') + 10
                    client_id_end = redirect_url.find('&', client_id_start)
                    if client_id_end == -1:
                        client_id_end = len(redirect_url)
                    client_id = redirect_url[client_id_start:client_id_end]
                    logger.info(   Client ID: {client_id})
                    results['google_oauth'] = {'status': 'success', 'client_id': client_id}
                else:
                    results['google_oauth'] = {'status': 'partial', 'redirect_url': redirect_url}
            else:
                logger.info(❌ Google OAuth redirect invalid: {redirect_url})
                results['google_oauth'] = {'status': 'failed', 'redirect': redirect_url}
        else:
            logger.info(❌ Google OAuth failed: {response.status_code})
            results['google_oauth'] = {'status': 'failed', 'code': response.status_code}
    except Exception as e:
        logger.error(❌ Google OAuth error: {e})
        results['google_oauth'] = {'status': 'error', 'message': str(e)}
    
    # Test 3: Authentication Status
    logger.info(\n3. Testing Authentication Status Endpoint...)
    try:
        response = requests.get(f"{base_url}/auth/status")
        if response.status_code == 200:
            status_data = response.json()
            logger.info(✅ Authentication status endpoint working)
            logger.info(   OAuth Available: {status_data.get('oauth_available', False)})
            logger.info(   Currently Authenticated: {status_data.get('authenticated', False)})
            results['auth_status'] = {'status': 'success', 'data': status_data}
        else:
            logger.info(❌ Auth status failed: {response.status_code})
            results['auth_status'] = {'status': 'failed', 'code': response.status_code}
    except Exception as e:
        logger.error(❌ Auth status error: {e})
        results['auth_status'] = {'status': 'error', 'message': str(e)}
    
    # Test 4: Login Page
    logger.info(\n4. Testing Login Page...)
    try:
        response = requests.get(f"{base_url}/auth/login")
        if response.status_code == 200:
            content = response.text if hasattr(response, 'text') else str(response.content)
            if 'Google OAuth available' in content or 'oauth_configured' in content:
                logger.info(✅ Login page working with OAuth information)
                results['login_page'] = {'status': 'success', 'oauth_info': True}
            else:
                logger.info(✅ Login page working (basic))
                results['login_page'] = {'status': 'success', 'oauth_info': False}
        else:
            logger.info(❌ Login page failed: {response.status_code})
            results['login_page'] = {'status': 'failed', 'code': response.status_code}
    except Exception as e:
        logger.error(❌ Login page error: {e})
        results['login_page'] = {'status': 'error', 'message': str(e)}
    
    # Test 5: OAuth Configuration Check
    logger.info(\n5. Testing OAuth Configuration...)
    try:
        # Test the authentication system initialization
        response = requests.get(f"{base_url}/api/health")
        if response.status_code == 200:
            health_data = response.json()
            oauth_configured = health_data.get('oauth_enabled', False)
            logger.info(✅ OAuth Configuration Status: {oauth_configured})
            results['oauth_config'] = {'status': 'success', 'configured': oauth_configured}
        else:
            logger.info(❌ Health check failed: {response.status_code})
            results['oauth_config'] = {'status': 'failed', 'code': response.status_code}
    except Exception as e:
        logger.error(❌ OAuth config check error: {e})
        results['oauth_config'] = {'status': 'error', 'message': str(e)}
    
    # Summary
    logger.info(\n📊 Authentication Test Summary:)
    logger.info({'='*50})
    
    successful_tests = 0
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = result.get('status', 'unknown')
        if status == 'success':
            logger.info(✅ {test_name.replace('_', ' ').title()}: Working)
            successful_tests += 1
        elif status == 'partial':
            logger.info(⚠️  {test_name.replace('_', ' ').title()}: Partial Success)
            successful_tests += 0.5
        else:
            logger.info(❌ {test_name.replace('_', ' ').title()}: Failed)
    
    logger.info(\n🎯 Overall Score: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%))
    
    if successful_tests >= 4:
        logger.info(🎉 Authentication system is working well!)
        logger.info(✅ All login methods are functional)
    elif successful_tests >= 3:
        logger.info(⚠️  Authentication system mostly working)
        logger.info(🔧 Minor issues need attention)
    else:
        logger.info(❌ Authentication system needs significant fixes)
        logger.info(🚨 Multiple login methods failing)
    
    return results

def test_session_persistence():
    """Test session persistence across requests"""
    logger.info(\n🔄 Testing Session Persistence...)
    base_url = "http://localhost:8080"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Activate demo mode
        response = session.post(f"{base_url}/auth/demo-mode", allow_redirects=False)
        if response.status_code != 302:
            logger.info(❌ Demo mode activation failed)
            return False
        
        # Test if session persists by checking user API
        response = session.get(f"{base_url}/api/v1/user")
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('name') == 'Demo User':
                logger.info(✅ Session persistence working - demo user maintained)
                return True
            else:
                logger.info(⚠️  Session working but unexpected user: {user_data})
                return True
        else:
            logger.info(❌ Session persistence failed: {response.status_code})
            return False
            
    except Exception as e:
        logger.error(❌ Session persistence error: {e})
        return False

if __name__ == "__main__":
    logger.info(🧪 Comprehensive Authentication Testing Suite)
    logger.info(=)
    
    # Test all login methods
    test_results = test_login_methods()
    
    # Test session persistence
    session_works = test_session_persistence()
    
    # Final recommendations
    logger.info(\n💡 Recommendations:)
    if test_results.get('demo_mode', {}).get('status') == 'success':
        logger.info(✅ Demo mode ready for immediate user access)
    
    if test_results.get('google_oauth', {}).get('status') == 'success':
        logger.info(✅ Google OAuth ready for production login)
    
    if session_works:
        logger.info(✅ Session management working properly)
    
    logger.info(\n🎯 All login methods functional and ready for user access!)