#!/usr/bin/env python3
"""
Fix Deployment OAuth Issues
Addresses common OAuth problems after redeployment
"""

import os
import sys

def fix_deployment_oauth():
    """Fix common OAuth deployment issues"""
    
    logger.info(🔧 Fixing Deployment OAuth Issues)
    logger.info(=)
    
    # Fix 1: Ensure OAuth route is properly configured for deployment
    logger.info(\n1. Updating OAuth routes for deployment...)
    
    auth_routes_content = '''#!/usr/bin/env python3
"""
Authentication Routes - Google OAuth Implementation
Provides secure Google login/logout functionality with deployment fixes
"""

import os
import logging
from flask import Blueprint, render_template, redirect, request, session, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from utils.google_oauth import oauth_service
from utils.rate_limiter import login_rate_limit, oauth_rate_limit
from models.user import User
from database import db

logger = logging.getLogger(__name__)

# Create auth blueprint with consistent naming
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    """Display login page with Google OAuth option"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Check if OAuth is configured
    if not oauth_service.is_configured():
        flash('Google OAuth is not configured. Please contact administrator.', 'error')
        return render_template('auth/login.html', oauth_available=False)
    
    return render_template('auth/login.html', oauth_available=True)

@auth_bp.route('/google')
@oauth_rate_limit
def google_login():
    """Initiate Google OAuth login with deployment-aware redirect URI"""
    if not oauth_service.is_configured():
        logger.warning("Google OAuth is not configured - missing credentials")
        flash('Google OAuth is not configured.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Get deployment-aware redirect URI
        redirect_uri = get_deployment_callback_uri()
        logger.info(f"Initiating OAuth with redirect URI: {redirect_uri}")
        return oauth_service.get_authorization_url(redirect_uri)
    except Exception as e:
        logger.error(f"OAuth initiation failed: {str(e)}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback with enhanced error handling"""
    try:
        # Get deployment-aware redirect URI for token exchange
        redirect_uri = get_deployment_callback_uri()
        
        # Handle OAuth callback
        user = oauth_service.handle_callback(redirect_uri)
        
        if user:
            login_user(user, remember=True)
            flash('Successfully logged in with Google!', 'success')
            
            # Redirect to intended page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Authentication failed. Please try again.', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        logger.error(f"OAuth callback failed: {str(e)}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout current user with CSRF protection"""
    try:
        oauth_service.logout()
        flash('You have been logged out.', 'info')
        return redirect(url_for('main.index'))
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        flash('Logout failed. Please try again.', 'error')
        return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Display user profile"""
    return render_template('auth/profile.html', user=current_user)

def get_deployment_callback_uri():
    """Get the correct callback URI for the current deployment environment"""
    
    # Try to get the deployment URL from various sources
    deployment_url = None
    
    # Check environment variables
    for env_var in ['REPL_URL', 'REPLIT_DOMAIN', 'REPL_SLUG']:
        if os.environ.get(env_var):
            deployment_url = os.environ.get(env_var)
            break
    
    # If no environment variable, try to construct from request
    if not deployment_url:
        try:
            from flask import request
            if request:
                # Get the host from the current request
                scheme = 'https' if request.is_secure else 'http'
                host = request.host
                deployment_url = f"{scheme}://{host}"
        except Exception as e:
    logger.error(f"Unexpected error: {e}")
    
    # Fallback to common Replit patterns
    if not deployment_url:
        # Try common Replit URL patterns
        possible_domains = [
            "https://nous.replit.app",
            "https://nous-assistant.replit.app", 
            "https://workspace.replit.dev"
        ]
        # Use the first one as fallback
        deployment_url = possible_domains[0]
        logger.warning(f"Using fallback deployment URL: {deployment_url}")
    
    callback_uri = f"{deployment_url}/auth/google/callback"
    logger.info(f"Using callback URI: {callback_uri}")
    
    return callback_uri

# Export the blueprint
__all__ = ['auth_bp']
'''
    
    # Write the updated auth routes
    with open('routes/auth_routes.py', 'w') as f:
        f.write(auth_routes_content)
    
    logger.info(   ✅ Updated auth routes with deployment-aware redirect URIs)
    
    # Fix 2: Update OAuth service to handle deployment URLs
    logger.info(\n2. Updating OAuth service for deployment compatibility...)
    
    # Read current OAuth service
    with open('utils/google_oauth.py', 'r') as f:
        oauth_content = f.read()
    
    # Add deployment URL detection function if not present
    if 'get_deployment_url' not in oauth_content:
        deployment_function = '''
    def get_deployment_url(self):
        """Get the current deployment URL"""
        import os
        from flask import request, has_request_context
        
        # Try environment variables first
        for env_var in ['REPL_URL', 'REPLIT_DOMAIN']:
            if os.environ.get(env_var):
                return os.environ.get(env_var)
        
        # Try to get from request context
        if has_request_context() and request:
            scheme = 'https' if request.is_secure else 'http'
            return f"{scheme}://{request.host}"
        
        # Fallback to common Replit URL
        return "https://nous.replit.app"
'''
        
        # Insert the function before the last line
        lines = oauth_content.split('\n')
        # Find the line with 'def user_loader' and insert before it
        for i, line in enumerate(lines):
            if 'def user_loader' in line:
                lines.insert(i, deployment_function)
                break
        
        oauth_content = '\n'.join(lines)
        
        with open('utils/google_oauth.py', 'w') as f:
            f.write(oauth_content)
        
        logger.info(   ✅ Added deployment URL detection to OAuth service)
    
    # Fix 3: Create a comprehensive redirect URI guide
    logger.info(\n3. Creating redirect URI configuration guide...)
    
    redirect_guide = '''# Google Cloud Console Redirect URI Configuration

## Required Redirect URIs

Add ALL of these redirect URIs to your Google Cloud Console OAuth 2.0 client:

### Replit Deployment URLs:
- https://nous.replit.app/auth/google/callback
- https://nous-assistant.replit.app/auth/google/callback
- https://workspace.replit.dev/auth/google/callback

### Common Replit Patterns:
- https://[YOUR-REPL-NAME].replit.app/auth/google/callback
- https://[YOUR-REPL-NAME].[YOUR-USERNAME].replit.app/auth/google/callback

### Development URLs (if testing locally):
- http://localhost:8080/auth/google/callback
- http://127.0.0.1:8080/auth/google/callback

## How to Configure:

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Select your project
3. Navigate to "APIs & Services" > "Credentials"
4. Click on your OAuth 2.0 Client ID
5. In "Authorized redirect URIs" section, add ALL the URLs above
6. Save the changes

## Troubleshooting:

If OAuth still doesn't work after adding redirect URIs:
1. Wait 5-10 minutes for Google's changes to propagate
2. Clear your browser cache and cookies
3. Try the OAuth flow again
4. Check that GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set in Replit Secrets

## Current Deployment:

To find your exact deployment URL:
1. Check the address bar when your app is running
2. Use that exact URL + "/auth/google/callback" as a redirect URI
'''
    
    with open('GOOGLE_OAUTH_SETUP.md', 'w') as f:
        f.write(redirect_guide)
    
    logger.info(   ✅ Created Google OAuth setup guide)
    
    # Fix 4: Test the OAuth configuration
    logger.info(\n4. Testing OAuth configuration...)
    
    try:
        from utils.google_oauth import oauth_service
        from flask import Flask
        
        app = Flask(__name__)
        app.secret_key = os.environ.get('SESSION_SECRET', 'test-secret')
        
        with app.app_context():
            if oauth_service.init_app(app):
                logger.info(   ✅ OAuth service initializes correctly)
                
                if oauth_service.is_configured():
                    logger.info(   ✅ OAuth service is properly configured)
                else:
                    logger.info(   ❌ OAuth service configuration failed)
            else:
                logger.info(   ❌ OAuth service initialization failed)
                
    except Exception as e:
        logger.info(   ❌ OAuth test failed: {e})
    
    logger.info(\n)
    logger.info(🎯 DEPLOYMENT OAUTH FIXES COMPLETE)
    logger.info(=)
    
    logger.info(\n✅ Applied Fixes:)
    logger.info(   • Updated auth routes with deployment-aware redirect URIs)
    logger.info(   • Enhanced OAuth service with deployment URL detection)
    logger.info(   • Created comprehensive redirect URI configuration guide)
    logger.info(   • Tested OAuth configuration)
    
    logger.info(\n🚀 Next Steps:)
    logger.info(   1. Redeploy your application)
    logger.info(   2. Find your exact deployment URL)
    logger.info(   3. Add the callback URI to Google Cloud Console:)
    logger.info(      [YOUR-DEPLOYMENT-URL]/auth/google/callback)
    logger.info(   4. Test the 'Sign in with Google' button)
    
    logger.info(\n📋 Quick Checklist:)
    logger.info(   □ Deployment URL found)
    logger.info(   □ Redirect URI added to Google Cloud Console)
    logger.info(   □ Application redeployed)
    logger.info(   □ OAuth tested and working)

if __name__ == "__main__":
    fix_deployment_oauth()