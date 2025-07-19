import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Complete Authentication System Test
Tests the full OAuth flow and authentication security
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_authentication_system():
    """Test the complete authentication system"""
    logger.info("Testing NOUS Authentication System")
    logger.info("=" * 50)
    
    # Test 1: Check environment variables (if provided)
    oauth_configured = (
        os.environ.get('GOOGLE_CLIENT_ID') and 
        os.environ.get('GOOGLE_CLIENT_SECRET')
    )
    
    logger.info(f"OAuth Credentials Configured: {'✅ Yes' if oauth_configured else '⚠️ No (will need to be provided)'}")
    
    # Test 2: Check User model for OAuth fields
    try:
        from models.user_models import User
        has_oauth_fields = all(hasattr(User, field) for field in ['google_id', 'is_active'])
        logger.info(f"User Model OAuth Fields: {'✅ Present' if has_oauth_fields else '❌ Missing'}")
    except Exception as e:
        logger.error(f"❌ Failed to import User model: {str(e)}")
        has_oauth_fields = False

    # Test 3: Check OAuth routes
    try:
        from app import app
        oauth_routes = ['/login/google', '/authorize/google', '/login/google/authorized']
        registered_routes = [rule.rule for rule in app.url_map.iter_rules()]
        missing_routes = [route for route in oauth_routes if route not in registered_routes]
        
        if missing_routes:
            logger.warning(f"⚠️ Missing OAuth routes: {', '.join(missing_routes)}")
        else:
            logger.info("✅ All OAuth routes are registered")
    except Exception as e:
        logger.error(f"❌ Error checking OAuth routes: {str(e)}")
        missing_routes = oauth_routes

    # Test 4: Check for session security settings
    try:
        from app import app
        secure_cookie = app.config.get('SESSION_COOKIE_SECURE', False)
        http_only = app.config.get('SESSION_COOKIE_HTTPONLY', False)
        same_site = app.config.get('SESSION_COOKIE_SAMESITE', 'Lax')
        
        logger.info("Session Security Settings:")
        logger.info(f"  - Secure: {'✅' if secure_cookie else '❌'}")
        logger.info(f"  - HTTP Only: {'✅' if http_only else '❌'}")
        logger.info(f"  - SameSite: {same_site}")
        
        session_secure = all([secure_cookie, http_only, same_site in ['Lax', 'Strict']])
    except Exception as e:
        logger.error(f"❌ Error checking session settings: {str(e)}")
        session_secure = False

    # Test 5: Check for CSRF protection
    try:
        from flask_wtf.csrf import CSRFProtect
        csrf_enabled = 'csrf' in app.extensions
        logger.info(f"CSRF Protection: {'✅ Enabled' if csrf_enabled else '❌ Disabled'}")
    except Exception as e:
        logger.error(f"❌ Error checking CSRF protection: {str(e)}")
        csrf_enabled = False

    # Test 6: Check for rate limiting
    try:
        from utils.rate_limiter import limiter
        rate_limiting_enabled = limiter.enabled
        logger.info(f"Rate Limiting: {'✅ Enabled' if rate_limiting_enabled else '❌ Disabled'}")
    except Exception as e:
        logger.error(f"❌ Error checking rate limiting: {str(e)}")
        rate_limiting_enabled = False

    # Print summary
    logger.info("\n" + "="*50)
    logger.info("Authentication System Test Summary")
    logger.info("="*50)
    logger.info(f"OAuth Configured: {'✅' if oauth_configured else '❌'}")
    logger.info(f"User Model: {'✅' if has_oauth_fields else '❌'}")
    logger.info(f"OAuth Routes: {'✅' if not missing_routes else '❌'}")
    logger.info(f"Session Security: {'✅' if session_secure else '❌'}")
    logger.info(f"CSRF Protection: {'✅' if csrf_enabled else '❌'}")
    logger.info(f"Rate Limiting: {'✅' if rate_limiting_enabled else '❌'}")
    logger.info("="*50 + "\n")

def validate_security_improvements():
    """Validate that all security fixes have been applied"""
    logger.info("Validating Security Improvements")
    logger.info("="*50)
    
    security_checks = {
        "Session Configuration": False,
        "CSRF Protection": False,
        "Rate Limiting": False,
        "Secure Headers": False,
        "Input Validation": False
    }
    
    # Check blueprint naming
    try:
        from routes.auth_routes import auth_bp
        if auth_bp.name == 'auth':
            security_checks["Blueprint Naming"] = True
    except Exception as e:
        logger.error(f"Unexpected error in blueprint naming check: {e}")
    
    # Check token refresh
    try:
        from utils.oauth_service import OAuthService
        if hasattr(OAuthService, 'refresh_access_token'):
            security_checks["Token Refresh"] = True
    except Exception as e:
        logger.error(f"Unexpected error in token refresh check: {e}")
    
    # Check CSRF protection
    try:
        from flask_wtf.csrf import CSRFProtect
        if 'csrf' in app.extensions:
            security_checks["CSRF Protection"] = True
    except Exception as e:
        logger.error(f"Unexpected error in CSRF check: {e}")
    
    # Check error handling
    try:
        from utils.error_handlers import handle_http_error
        if callable(handle_http_error):
            security_checks["Error Handling"] = True
    except Exception as e:
        logger.error(f"Unexpected error in error handling check: {e}")
    
    # Check demo mode security
    try:
        from config import Config
        if not Config.DEBUG and not Config.TESTING:
            security_checks["Demo Mode Security"] = True
    except Exception as e:
        logger.error(f"Unexpected error in demo mode check: {e}")
    
    # Check username collision handling
    try:
        from models.user_models import User
        if hasattr(User, 'find_by_username'):
            security_checks["Username Collision"] = True
    except Exception as e:
        logger.error(f"Unexpected error in username collision check: {e}")
    
    # Check OAuth token storage
    try:
        from models.user_models import User
        if hasattr(User, 'google_refresh_token'):
            security_checks["OAuth Token Storage"] = True
    except Exception as e:
        logger.error(f"Unexpected error in OAuth token check: {e}")
    
    # Print results
    logger.info("\nSecurity Checks Summary:")
    logger.info("="*50)
    for check, status in security_checks.items():
        status_icon = 'PASS' if status else 'FAIL'
        logger.info("{}: {}".format(check, status_icon))
    
    if all(security_checks.values()):
        logger.info("\nAll security checks passed!")
    else:
        logger.warning("\nSome security checks failed. Please review the logs above.")
    
    logger.info("="*50 + "\n")
    logger.info("SECURITY VALIDATION REPORT")
    logger.info("="*50)
    
    security_fixes = {
        "Blueprint Naming": False,
        "Token Refresh": False,
        "CSRF Protection": False,
        "Error Handling": False,
        "Demo Mode Security": False,
        "Username Collision": False,
        "OAuth Token Storage": False
    }
    
    for fix_name, is_fixed in security_fixes.items():
        status = "FIXED" if is_fixed else "PENDING"
        logger.info("{}: {}".format(fix_name.replace('_', ' ').title(), status))
    
    fixed_count = sum(security_fixes.values())
    total_count = len(security_fixes)
    security_score = (fixed_count / total_count) * 100 if total_count > 0 else 0
    
    logger.info("\nSecurity Score: {:.1f}%".format(security_score))
    
    if security_score >= 90:
        logger.info("Excellent security posture!")
    elif security_score >= 70:
        logger.info("Good security posture, but some improvements needed.")
    else:
        logger.warning("Security posture needs immediate attention!")
    
    return security_score

if __name__ == '__main__':
    test_authentication_system()
    logger.info("\n")
    validate_security_improvements()