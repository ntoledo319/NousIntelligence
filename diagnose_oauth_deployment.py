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
    
    print("🔍 OAuth Deployment Issue Diagnosis")
    print("=" * 50)
    
    issues_found = []
    
    # Issue 1: Check environment variables
    print("\n1. Environment Variables Check:")
    required_vars = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'SESSION_SECRET']
    
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"   {var}: ✅ Set")
        else:
            print(f"   {var}: ❌ Missing")
            issues_found.append(f"Missing environment variable: {var}")
    
    # Issue 2: Check OAuth service initialization
    print("\n2. OAuth Service Initialization:")
    try:
        sys.path.append('.')
        from utils.google_oauth import oauth_service
        
        if oauth_service:
            print("   OAuth Service: ✅ Exists")
        else:
            print("   OAuth Service: ❌ Not found")
            issues_found.append("OAuth service not initialized")
            
        # Test in Flask context
        from flask import Flask
        app = Flask(__name__)
        app.secret_key = os.environ.get('SESSION_SECRET', 'fallback-secret')
        
        with app.app_context():
            init_success = oauth_service.init_app(app)
            if init_success:
                print("   OAuth Initialization: ✅ Success")
            else:
                print("   OAuth Initialization: ❌ Failed")
                issues_found.append("OAuth initialization failed")
                
            if oauth_service.google:
                print("   Google Client: ✅ Created")
            else:
                print("   Google Client: ❌ Not created")
                issues_found.append("Google OAuth client not created")
                
    except Exception as e:
        print(f"   OAuth Service Error: ❌ {e}")
        issues_found.append(f"OAuth service error: {e}")
    
    # Issue 3: Check deployment configuration
    print("\n3. Deployment Configuration:")
    
    # Check .replit file exists
    if os.path.exists('.replit'):
        print("   .replit file: ✅ Exists")
    else:
        print("   .replit file: ❌ Missing")
        issues_found.append(".replit configuration file missing")
    
    # Check gunicorn config
    if os.path.exists('gunicorn.conf.py'):
        print("   Gunicorn config: ✅ Exists")
    else:
        print("   Gunicorn config: ❌ Missing")
        issues_found.append("Gunicorn configuration missing")
    
    # Issue 4: Check OAuth routes
    print("\n4. OAuth Routes Check:")
    try:
        from routes.auth_routes import auth_bp
        if auth_bp:
            print("   Auth blueprint: ✅ Exists")
            
            # Check route registration
            routes = [rule.rule for rule in auth_bp.url_map.iter_rules()]
            google_route = any('/google' in route for route in routes)
            callback_route = any('/callback' in route for route in routes)
            
            print(f"   Google login route: {'✅ Found' if google_route else '❌ Missing'}")
            print(f"   Callback route: {'✅ Found' if callback_route else '❌ Missing'}")
            
            if not google_route:
                issues_found.append("Google login route not found")
            if not callback_route:
                issues_found.append("OAuth callback route not found")
        else:
            print("   Auth blueprint: ❌ Not found")
            issues_found.append("Auth blueprint not found")
            
    except Exception as e:
        print(f"   Route check error: ❌ {e}")
        issues_found.append(f"Route check failed: {e}")
    
    # Issue 5: Check redirect URI configuration
    print("\n5. Redirect URI Analysis:")
    
    # Common deployment URLs
    possible_urls = [
        "https://workspace.replit.dev",
        "https://nous.replit.app", 
        "https://nous-assistant.replit.app",
        "https://replit.dev",
        "https://replit.app"
    ]
    
    print("   Possible deployment URLs:")
    for url in possible_urls:
        print(f"     • {url}")
    
    print("\n   Required redirect URIs for Google Cloud Console:")
    for url in possible_urls:
        print(f"     • {url}/auth/google/callback")
    
    # Issue 6: Common OAuth problems
    print("\n6. Common OAuth Problems:")
    common_issues = [
        "Redirect URI mismatch in Google Cloud Console",
        "Missing OAuth credentials in Replit Secrets",
        "OAuth client not properly initialized in Flask app",
        "Blueprint registration order issues",
        "Rate limiting blocking OAuth requests",
        "SSL/HTTPS certificate issues in deployment"
    ]
    
    for issue in common_issues:
        print(f"   • {issue}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSIS SUMMARY")
    print("=" * 50)
    
    if issues_found:
        print("❌ Issues Found:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
            
        print("\n🔧 Recommended Fixes:")
        if any("environment" in issue.lower() for issue in issues_found):
            print("   • Add missing environment variables to Replit Secrets")
        if any("oauth" in issue.lower() for issue in issues_found):
            print("   • Restart the deployment to reload OAuth configuration")
        if any("route" in issue.lower() for issue in issues_found):
            print("   • Check blueprint registration in routes/__init__.py")
        
        print("   • Verify redirect URIs in Google Cloud Console")
        print("   • Check application logs for detailed error messages")
        
    else:
        print("✅ No obvious issues detected")
        print("   OAuth should be working. Check Google Cloud Console redirect URIs.")

if __name__ == "__main__":
    try:
        diagnose_oauth_issues()
    except Exception as e:
        print(f"Diagnosis failed: {e}")
        traceback.print_exc()