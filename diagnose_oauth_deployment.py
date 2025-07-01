import logging
logger = logging.getLogger(__name__)
#!/usr/bin/env python3
"""
Diagnose OAuth Deployment Issues
Identify why OAuth isn't working after redeployment
"""

import os
import sys
import traceback

def diagnose_oauth_issues():
    """Diagnose common OAuth deployment issues"""
    
    logger.info(🔍 OAuth Deployment Issue Diagnosis)
    logger.info(=)
    
    issues_found = []
    
    # Issue 1: Check environment variables
    logger.info(\n1. Environment Variables Check:)
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'SESSION_SECRET']
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            logger.info(   {var}: ✅ Set)
        else:
            logger.info(   {var}: ❌ Missing)
            issues_found.append(f"Missing environment variable: {var}")
    
    # Issue 2: Check OAuth service initialization
    logger.info(\n2. OAuth Service Initialization:)
    try:
        sys.path.append('.')
        from utils.google_oauth import oauth_service
        
        if oauth_service:
            logger.info(   OAuth Service: ✅ Exists)
        else:
            logger.info(   OAuth Service: ❌ Not found)
            issues_found.append("OAuth service not initialized")
            
        # Test in Flask context
        from flask import Flask
        app = Flask(__name__)
        app.secret_key = os.environ.get('SESSION_SECRET', 'fallback-secret')
        
        with app.app_context():
            init_success = oauth_service.init_app(app)
            if init_success:
                logger.info(   OAuth Initialization: ✅ Success)
            else:
                logger.info(   OAuth Initialization: ❌ Failed)
                issues_found.append("OAuth initialization failed")
                
            if oauth_service.google:
                logger.info(   Google Client: ✅ Created)
            else:
                logger.info(   Google Client: ❌ Not created)
                issues_found.append("Google OAuth client not created")
                
    except Exception as e:
        logger.error(   OAuth Service Error: ❌ {e})
        issues_found.append(f"OAuth service error: {e}")
    
    # Issue 3: Check deployment configuration
    logger.info(\n3. Deployment Configuration:)
    
    # Check .replit file exists
    if os.path.exists('.replit'):
        logger.info(   .replit file: ✅ Exists)
    else:
        logger.info(   .replit file: ❌ Missing)
        issues_found.append(".replit configuration file missing")
    
    # Check gunicorn config
    if os.path.exists('gunicorn.conf.py'):
        logger.info(   Gunicorn config: ✅ Exists)
    else:
        logger.info(   Gunicorn config: ❌ Missing)
        issues_found.append("Gunicorn configuration missing")
    
    # Issue 4: Check OAuth routes
    logger.info(\n4. OAuth Routes Check:)
    try:
        from routes.auth_routes import auth_bp
        if auth_bp:
            logger.info(   Auth blueprint: ✅ Exists)
            
            # Check route registration
            routes = [rule.rule for rule in auth_bp.url_map.iter_rules()]
            google_route = any('/google' in route for route in routes)
            callback_route = any('/callback' in route for route in routes)
            
            logger.info(   Google login route: {'✅ Found' if google_route else '❌ Missing'})
            logger.info(   Callback route: {'✅ Found' if callback_route else '❌ Missing'})
            
            if not google_route:
                issues_found.append("Google login route not found")
            if not callback_route:
                issues_found.append("OAuth callback route not found")
        else:
            logger.info(   Auth blueprint: ❌ Not found)
            issues_found.append("Auth blueprint not found")
            
    except Exception as e:
        logger.error(   Route check error: ❌ {e})
        issues_found.append(f"Route check failed: {e}")
    
    # Issue 5: Check redirect URI configuration
    logger.info(\n5. Redirect URI Analysis:)
    
    # Common deployment URLs
    possible_urls = [
        "https://workspace.replit.dev",
        "https://nous.replit.app", 
        "https://nous-assistant.replit.app",
        "https://replit.dev",
        "https://replit.app"
    ]
    
    logger.info(   Possible deployment URLs:)
    for url in possible_urls:
        logger.info(     • {url})
    
    logger.info(\n   Required redirect URIs for Google Cloud Console:)
    for url in possible_urls:
        logger.info(     • {url}/auth/google/callback)
    
    # Issue 6: Common OAuth problems
    logger.info(\n6. Common OAuth Problems:)
    common_issues = [
        "Redirect URI mismatch in Google Cloud Console",
        "Missing OAuth credentials in Replit Secrets",
        "OAuth client not properly initialized in Flask app",
        "Blueprint registration order issues",
        "Rate limiting blocking OAuth requests",
        "SSL/HTTPS certificate issues in deployment"
    ]
    
    for issue in common_issues:
        logger.info(   • {issue})
    
    # Summary
    logger.info(\n)
    logger.info(📊 DIAGNOSIS SUMMARY)
    logger.info(=)
    
    if issues_found:
        logger.info(❌ Issues Found:)
        for i, issue in enumerate(issues_found, 1):
            logger.info(   {i}. {issue})
            
        logger.info(\n🔧 Recommended Fixes:)
        if any("environment" in issue.lower() for issue in issues_found):
            logger.info(   • Add missing environment variables to Replit Secrets)
        if any("oauth" in issue.lower() for issue in issues_found):
            logger.info(   • Restart the deployment to reload OAuth configuration)
        if any("route" in issue.lower() for issue in issues_found):
            logger.info(   • Check blueprint registration in routes/__init__.py)
        
        logger.info(   • Verify redirect URIs in Google Cloud Console)
        logger.error(   • Check application logs for detailed error messages)
        
    else:
        logger.info(✅ No obvious issues detected)
        logger.info(   OAuth should be working. Check Google Cloud Console redirect URIs.)

if __name__ == "__main__":
    try:
        diagnose_oauth_issues()
    except Exception as e:
        logger.info(Diagnosis failed: {e})
        traceback.print_exc()