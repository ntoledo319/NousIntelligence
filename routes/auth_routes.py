"""
Authentication Routes
Secure Google OAuth 2.0 authentication system for NOUS application
"""

from flask import Blueprint, redirect, url_for, request, flash, session, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from utils.google_oauth import oauth_service
from config.app_config import AppConfig

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login')
def login():
    """Initiate Google OAuth login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if not oauth_service.is_configured():
        flash('Google OAuth is not configured. Please contact administrator.', 'error')
        return redirect(url_for('main.landing'))
    
    # Store the next URL for redirect after login
    next_url = request.args.get('next')
    if next_url:
        session['next'] = next_url
    
    # Create callback URL
    redirect_uri = url_for('auth.callback', _external=True)
    
    return oauth_service.get_authorization_url(redirect_uri)


@auth_bp.route('/callback')
def callback():
    """Handle Google OAuth callback"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    try:
        # Handle OAuth callback
        redirect_uri = url_for('auth.callback', _external=True)
        user = oauth_service.handle_callback(redirect_uri)
        
        if user:
            flash(f'Welcome, {user.username}!', 'success')
            
            # Redirect to originally requested page or dashboard
            next_url = session.pop('next', None)
            return redirect(next_url or url_for('main.dashboard'))
        else:
            flash('Login failed. Please try again.', 'error')
            return redirect(url_for('main.landing'))
            
    except Exception as e:
        flash(f'Login error: {str(e)}', 'error')
        return redirect(url_for('main.landing'))


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout current user"""
    username = current_user.username if current_user.is_authenticated else 'User'
    oauth_service.logout()
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('main.landing'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None,
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None,
            'google_connected': bool(current_user.google_id)
        }
    })


@auth_bp.route('/status')
def status():
    """Authentication status check"""
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'oauth_configured': oauth_service.is_configured(),
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email
        } if current_user.is_authenticated else None
    })


@auth_bp.route('/demo-mode')
def demo_mode():
    """Enable demo mode for testing without authentication"""
    if AppConfig.DEBUG:
        # In debug mode, allow demo mode for testing
        from utils.auth_compat import get_demo_user
        demo_user = get_demo_user()
        session['demo_user'] = True
        flash('Demo mode enabled', 'info')
        return redirect(url_for('main.dashboard'))
    else:
        flash('Demo mode not available in production', 'error')
        return redirect(url_for('main.landing'))