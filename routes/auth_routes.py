from utils.auth_compat import require_authentication, is_authenticated, get_current_user
#!/usr/bin/env python3
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

@auth_bp.route('/logout', methods=['POST'])
@require_authentication
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
@require_authentication
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
        except:
            pass
    
    # Fallback to common Replit patterns based on existing Google Cloud Console config
    if not deployment_url:
        # Check if we're on mynous.replit.app deployment
        try:
            from flask import request
            if request and 'mynous' in request.host:
                deployment_url = "https://mynous.replit.app"
            elif request and 'worf.replit.dev' in request.host:
                # Use the dynamic worf URL pattern
                deployment_url = f"https://{request.host}"
            else:
                # Default fallback
                deployment_url = "https://mynous.replit.app"
        except:
            deployment_url = "https://mynous.replit.app"
    
    # Use /callback/google format to match existing Google Cloud Console configuration
    callback_uri = f"{deployment_url}/callback/google"
    logger.info(f"Using callback URI: {callback_uri}")
    
    return callback_uri

# Export the blueprint
__all__ = ['auth_bp']
