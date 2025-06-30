#!/usr/bin/env python3
"""
Authentication Routes - Google OAuth Implementation
Provides secure Google login/logout functionality with deployment fixes
"""

import os
import logging
from flask import Blueprint, render_template, redirect, request, session, url_for, flash, jsonify

logger = logging.getLogger(__name__)

# Safe imports with fallbacks
try:
    from utils.google_oauth import oauth_service
except ImportError:
    oauth_service = None

try:
    from flask_login import login_user, logout_user, current_user
except ImportError:
    # Fallback functions for when Flask-Login is not available
    def login_user(user, remember=False):
        session['user_id'] = user.id
        session['user'] = user.to_dict()
        return True
    
    def logout_user():
        session.pop('user_id', None)
        session.pop('user', None)
    
    current_user = None

try:
    from utils.rate_limiter import login_rate_limit, oauth_rate_limit
except ImportError:
    # Fallback decorators
    def login_rate_limit(f):
        return f
    def oauth_rate_limit(f):
        return f

# Create auth blueprint with consistent naming
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    """Display login page with Google OAuth option"""
    # Check session authentication
    if session.get('user'):
        return redirect('/dashboard')
    
    # Check if OAuth is configured
    try:
        oauth_configured = oauth_service.is_configured() if oauth_service else False
    except:
        oauth_configured = False
    
    if not oauth_configured:
        # For demo, redirect to demo mode
        session['user'] = {
            'id': 'demo_user_123',
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'demo_mode': True
        }
        return redirect('/chat')
    
    return jsonify({"message": "Google OAuth available", "oauth_configured": True})

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
@auth_bp.route('/callback/google')  # Support existing Google Cloud Console configuration
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

@auth_bp.route('/demo-mode', methods=['POST'])
def demo_mode():
    """Activate demo mode - provides immediate access without authentication"""
    try:
        # Create demo user session
        session['user'] = {
            'id': 'demo_user_123',
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'demo_mode': True,
            'avatar': '/static/images/default-avatar.png'
        }
        
        logger.info("Demo mode activated successfully")
        return redirect('/dashboard')
        
    except Exception as e:
        logger.error(f"Demo mode activation failed: {e}")
        flash('Failed to activate demo mode. Please try again.', 'error')
        return redirect('/')

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout current user with CSRF protection"""
    try:
        if oauth_service:
            oauth_service.logout()
        # Clear session
        session.pop('user', None)
        flash('You have been logged out.', 'info')
        return redirect('/')
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        flash('Logout failed. Please try again.', 'error')
        return redirect('/')

@auth_bp.route('/status')
def auth_status():
    """Get authentication status"""
    user_data = session.get('user')
    
    # Properly check OAuth configuration
    oauth_configured = False
    if oauth_service:
        try:
            oauth_configured = oauth_service.is_configured()
        except Exception as e:
            logger.error(f"Error checking OAuth configuration: {e}")
            oauth_configured = False
    
    return jsonify({
        'authenticated': user_data is not None,
        'user': user_data,
        'oauth_available': oauth_configured
    })

@auth_bp.route('/profile')
def profile():
    """Display user profile"""
    user_data = session.get('user', {})
    return render_template('auth/profile.html', user=user_data)

def get_deployment_callback_uri():
    """Get the correct callback URI for the current deployment environment"""
    
    deployment_url = None
    
    # First try to get from Flask request context
    try:
        from flask import request, has_request_context
        if has_request_context() and request:
            # Get the host from the current request
            scheme = 'https' if request.is_secure else 'http'
            host = request.host
            deployment_url = f"{scheme}://{host}"
            logger.info(f"Got deployment URL from request: {deployment_url}")
    except Exception as e:
        logger.debug(f"Could not get URL from request: {e}")
    
    # If no request context, check environment variables
    if not deployment_url:
        for env_var in ['REPL_URL', 'REPLIT_DOMAIN']:
            env_value = os.environ.get(env_var)
            if env_value:
                # Ensure it starts with https://
                if not env_value.startswith('http'):
                    deployment_url = f"https://{env_value}"
                else:
                    deployment_url = env_value
                logger.info(f"Got deployment URL from {env_var}: {deployment_url}")
                break
    
    # Final fallback - use localhost for testing
    if not deployment_url:
        deployment_url = "http://localhost:8080"
        logger.warning(f"Using fallback deployment URL: {deployment_url}")
    
    # Use /callback/google format to match existing Google Cloud Console configuration
    callback_uri = f"{deployment_url}/callback/google"
    logger.info(f"Final callback URI: {callback_uri}")
    
    return callback_uri

# Export the blueprint
__all__ = ['auth_bp']
