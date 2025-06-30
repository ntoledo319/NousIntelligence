
#!/usr/bin/env python3
"""
Authentication Routes - Google OAuth Implementation
Provides secure Google login/logout functionality
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
    """Initiate Google OAuth login"""
    if not oauth_service.is_configured():
        logger.warning("Google OAuth is not configured - missing credentials")
        flash('Google OAuth is not configured.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        redirect_uri = url_for('auth.google_callback', _external=True)
        logger.info(f"Initiating OAuth with redirect URI: {redirect_uri}")
        return oauth_service.get_authorization_url(redirect_uri)
    except Exception as e:
        logger.error(f"OAuth initiation failed: {str(e)}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/google/callback')
@oauth_rate_limit
def google_callback():
    """Handle Google OAuth callback"""
    try:
        redirect_uri = url_for('auth.google_callback', _external=True)
        user = oauth_service.handle_callback(redirect_uri)
        
        if user:
            login_user(user, remember=True)
            flash('Successfully logged in with Google!', 'success')
            
            # Redirect to originally requested page or dashboard
            next_page = session.get('next')
            if next_page:
                session.pop('next', None)
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Authentication failed. Please try again.', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        logger.error(f"Authentication callback failed: {str(e)}")
        logger.error(f"Request args: {request.args}")
        logger.error(f"Session state: {session.get('oauth_state', 'No state found')}")
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Logout current user - POST only for CSRF protection"""
    try:
        logout_user()
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('main.index'))
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        flash('Logout failed. Please try again.', 'error')
        return redirect(url_for('main.dashboard'))

@auth_bp.route('/demo-mode', methods=['POST'])
def demo_mode():
    """Enable demo mode - POST only and requires environment variable"""
    # Check if demo mode is enabled via environment variable
    if not os.environ.get('ENABLE_DEMO_MODE') == 'true':
        flash('Demo mode is not available.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Create demo session
        session['demo_user'] = {
            'id': 'demo_user',
            'name': 'Demo User',
            'email': 'demo@example.com',
            'is_demo': True
        }
        flash('Demo mode activated. Some features may be limited.', 'info')
        return redirect(url_for('main.dashboard'))
    except Exception as e:
        logger.error(f"Demo mode activation failed: {str(e)}")
        flash('Demo mode failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/status')
def auth_status():
    """Get authentication status - API endpoint"""
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'oauth_configured': oauth_service.is_configured(),
        'demo_available': os.environ.get('ENABLE_DEMO_MODE') == 'true'
    })
