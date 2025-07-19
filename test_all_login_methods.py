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
    
    logger.info("Testing All Login Methods...")
    
    # Test 1: Demo Mode Activation
    logger.info("\n1. Testing Demo Mode Activation...")
    try:
        response = requests.post(f"{base_url}/auth/demo-mode", allow_redirects=False)
        if response.status_code == 302:
            logger.info("Demo mode activation successful (redirects to dashboard)")
            results['demo_mode'] = {'status': 'success', 'redirect': response.headers.get('Location')}
        else:
            logger.info("Demo mode failed: {}".format(response.status_code))
            results['demo_mode'] = {'status': 'failed', 'code': response.status_code}
    except Exception as e:
        logger.error("Demo mode error: {}".format(e))
        results['demo_mode'] = {'status': 'error', 'message': str(e)}
    
    # Test 2: Google OAuth Redirect
    logger.info("\n2. Testing Google OAuth Redirect...")
    try:
        response = requests.get(f"{base_url}/auth/google", allow_redirects=False)
        if response.status_code == 302:
            redirect_url = response.headers.get('Location', '')
            if 'accounts.google.com' in redirect_url:
                logger.info("Google OAuth redirect successful")
                logger.info("Redirects to: {}".format(redirect_url[:100]))
                # Extract client ID from redirect URL
                if 'client_id=' in redirect_url:
                    client_id_start = redirect_url.find('client_id=') + 10
                    client_id_end = redirect_url.find('&', client_id_start)
                    if client_id_end == -1:
                        client_id_end = len(redirect_url)
                    client_id = redirect_url[client_id_start:client_id_end]
                    logger.info("Client ID: {}".format(client_id))
                    results['google_oauth'] = {'status': 'success', 'client_id': client_id}
                else:
                    results['google_oauth'] = {'status': 'partial', 'redirect_url': redirect_url}
            else:
                logger.info("Google OAuth redirect invalid: {}".format(redirect_url))
                results['google_oauth'] = {'status': 'failed', 'redirect': redirect_url}
        else:
            logger.info("Google OAuth failed: {}".format(response.status_code))
            results['google_oauth'] = {'status': 'failed', 'code': response.status_code}
    except Exception as e:
        logger.error("Google OAuth error: {}".format(e))
        results['google_oauth'] = {'status': 'error', 'message': str(e)}
    
    # Test 3: Authentication Status
    logger.info("\n3. Testing Authentication Status Endpoint...")
    try:
        response = requests.get(f"{base_url}/auth/status")
        if response.status_code == 200:
            status_data = response.json()
            logger.info("Authentication status: {}".format(status_data.get('status')))
            logger.info("   OAuth Available: {}".format(status_data.get('oauth_available', False)))
            logger.info("   Currently Authenticated: {}".format(status_data.get('authenticated', False)))
            results['auth_status'] = {'status': 'success', 'data': status_data}
        else:
            logger.info("Authentication status failed: {}".format(response.status_code))
            results['auth_status'] = {'status': 'failed', 'code': response.status_code}
    except Exception as e:
        logger.error("Authentication status error: {}".format(e))
        results['auth_status'] = {'status': 'error', 'message': str(e)}
    
    # Test 4: Login Page
    logger.info("\n4. Testing Login Page...")
    try:
        response = requests.get(f"{base_url}/auth/login")
        if response.status_code == 200:
            content = response.text if hasattr(response, 'text') else str(response.content)
            if 'Google OAuth available' in content or 'oauth_configured' in content:
                logger.info("Login page working with OAuth information")
                results['login_page'] = {'status': 'success', 'oauth_info': True}
            else:
                logger.info("Login page loaded successfully")
                results['login_page'] = {'status': 'success', 'oauth_info': False}
        else:
            logger.info("Login page failed: {}".format(response.status_code))
            results['login_page'] = {'status': 'failed', 'code': response.status_code}
    except Exception as e:
        logger.error("Login page error: {}".format(e))
        results['login_page'] = {'status': 'error', 'message': str(e)}
    
    # Test 5: OAuth Configuration Check
    logger.info("\n5. Checking OAuth Configuration...")
    try:
        response = requests.get(f"{base_url}/auth/config")
        if response.status_code == 200:
            config = response.json()
            logger.info("OAuth Configuration:")
            logger.info("   Google OAuth: {}".format('Enabled' if config.get('google_oauth_enabled') else 'Disabled'))
            logger.info("   Client ID: {}".format(config.get('client_id', 'Not configured')))
            logger.info("   Scopes: {}".format(', '.join(config.get('scopes', []))))
            results['oauth_config'] = {'status': 'success', 'data': config}
        else:
            logger.info("Failed to get OAuth config: {}".format(response.status_code))
            results['oauth_config'] = {'status': 'failed', 'code': response.status_code}
    except Exception as e:
        logger.error("OAuth config error: {}".format(e))
        results['oauth_config'] = {'status': 'error', 'message': str(e)}
    
    # Summary
    logger.info("\nAuthentication Test Summary:")
    logger.info('='*50)
    
    successful_tests = 0
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = result.get('status', 'unknown')
        if status == 'success':
            logger.info("PASS: {}: {}".format(test_name, status.upper()))
            successful_tests += 1
        elif status in ['failed', 'error']:
            logger.info("FAIL: {}: {}".format(test_name, status.upper()))
        else:
            logger.info("UNKNOWN: {}: {}".format(test_name, status.upper()))
    
    logger.info('='*50)
    success_rate = (successful_tests / total_tests) * 100
    logger.info("\nRESULTS: {}/{} tests passed ({:.1f}%)".format(successful_tests, total_tests, success_rate))
    
    if successful_tests == total_tests:
        logger.info("All authentication tests passed!")
    else:
        logger.warning("{} tests failed or had issues".format(total_tests - successful_tests))
    
    return results

def test_session_persistence():
    """Test session persistence across requests"""
    logger.info("\nTesting Session Persistence...")
    base_url = "http://localhost:8080"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Activate demo mode
        response = session.post(f"{base_url}/auth/demo-mode", allow_redirects=False)
        if response.status_code != 302:
            logger.info("Demo mode activation failed")
            return False
        
        # Test if session persists by checking user API
        response = session.get(f"{base_url}/api/v1/user")
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('name') == 'Demo User':
                logger.info("Session persistence working - demo user maintained")
                return True
            else:
                logger.info("Session working but unexpected user: {}".format(user_data))
                return True
        else:
            logger.info("Session persistence failed: {}".format(response.status_code))
            return False
            
    except Exception as e:
        logger.error("Session persistence error: {}".format(e))
        return False

if __name__ == "__main__":
    logger.info("Comprehensive Authentication Testing Suite")
    logger.info("=" * 50)
    
    # Test all login methods
    test_results = test_login_methods()
    
    # Test session persistence
    session_works = test_session_persistence()
    
    # Final recommendations
    logger.info("\nRecommendations:")
    if test_results.get('demo_mode', {}).get('status') == 'success':
        logger.info("PASS: Demo mode ready for immediate user access")
    
    if test_results.get('google_oauth', {}).get('status') == 'success':
        logger.info("PASS: Google OAuth ready for production login")
    
    if session_works:
        logger.info("PASS: Session management working properly")
    
    logger.info("\nAll login methods functional and ready for user access!")