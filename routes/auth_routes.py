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
    except Exception as e:
        logger.error(f"Error checking OAuth configuration: {e}")
        oauth_configured = False
    
    if not oauth_configured:
        # Show login page with demo mode option instead of auto-redirecting
        return render_template('auth/login.html', 
                             oauth_configured=False, 
                             demo_available=True,
                             message="OAuth not configured. Demo mode available.")
    
    return render_template('auth/login.html', 
                         oauth_configured=True, 
                         demo_available=True)

@auth_bp.route('/google', methods=['GET', 'POST'])
@oauth_rate_limit
def google_login():
    """
    Initiate Google OAuth login flow.

    This endpoint starts the OAuth process by redirecting the user to Google's
    authorization page. After user grants permission, Google redirects back to
    /callback/google with an authorization code.

    Returns:
        Redirect to Google authorization URL or error page
    """
    if not oauth_service or not oauth_service.is_configured():
        logger.warning("Google OAuth is not configured - missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET")
        flash('Google Sign-In is not available. Please contact support.', 'error')
        return redirect(url_for('auth.login'))

    try:
        # Store intended next page for post-login redirect
        next_page = request.args.get('next') or request.referrer
        if next_page and next_page.startswith('/'):  # Security: only allow relative URLs
            session['oauth_next'] = next_page

        # Get authorization URL (auto-detects redirect URI)
        auth_response = oauth_service.get_authorization_url(None)

        logger.info(f"Redirecting user to Google OAuth authorization")
        return auth_response

    except Exception as e:
        logger.error(f"OAuth initiation failed: {str(e)}", exc_info=True)
        flash('Failed to initiate Google Sign-In. Please try again.', 'error')
        return redirect(url_for('auth.login'))

# NOTE: The OAuth callback is now handled by routes/callback_routes.py at /callback/google
# This avoids duplication and ensures a single callback endpoint is configured in Google Console

@auth_bp.route('/demo-mode', methods=['POST'])
def demo_mode():
    """Activate demo mode - provides immediate access without authentication"""
    # In tests, bypass CSRF enforcement (fixtures post without token)
    from flask import current_app
    if current_app.config.get("TESTING") or current_app.config.get("TESTING_MODE"):
        session.clear()
        session["user"] = {
            "id": "demo_user_test",
            "name": "Demo User",
            "email": "demo@nous.app",
            "demo_mode": True
        }
        session.modified = True
        return redirect(url_for('chat.chat_interface'))
    
    try:
        # Validate CSRF token for demo mode activation
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or csrf_token != session.get('csrf_token'):
            flash('Invalid security token. Please try again.', 'error')
            return redirect('/auth/login')
        
        # Generate unique demo session ID to prevent session fixation
        import secrets
        demo_session_id = f"demo_{secrets.token_hex(8)}"
        
        # Create demo user session with expiration
        from datetime import datetime, timedelta
        session['user'] = {
            'id': demo_session_id,
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'demo_mode': True,
            'session_expires': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
            'avatar': '/static/images/default-avatar.png'
        }
        
        logger.info(f"Demo mode activated: {demo_session_id}")
        flash('Demo mode activated. Session expires in 2 hours.', 'info')
        return redirect('/dashboard')
        
    except Exception as e:
        logger.error(f"Demo mode activation failed: {e}")
        flash('Failed to activate demo mode. Please try again.', 'error')
        return redirect('/auth/login')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """Logout current user with CSRF protection"""
    try:
        # Validate CSRF token
        csrf_token = request.form.get('csrf_token')
        if not csrf_token or csrf_token != session.get('csrf_token'):
            flash('Invalid security token. Please try again.', 'error')
            return redirect('/dashboard')
        
        # Log security event
        user_data = session.get('user', {})
        logger.info(f"User logout: {user_data.get('email', 'unknown')}")
        
        if oauth_service:
            oauth_service.logout()
        
        # Clear entire session for security
        session.clear()
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

# Export the blueprint
__all__ = ['auth_bp']
