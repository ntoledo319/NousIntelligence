"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, current_user, get_current_user, is_authenticated
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_current_user():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

Settings View Routes

This module contains view routes for the settings page.

@module routes.view.settings
@author NOUS Development Team
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session

from models import ConversationDifficulty
from utils.security_helper import rate_limit
from services.settings import SettingsService

# Create blueprint
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

# Initialize service
settings_service = SettingsService()

@settings_bp.route('', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def settings_page():
    """Display user settings page"""
    # Get settings for the current user or session
    settings = settings_service.get_settings_for_user_or_session(session.get('user'))

    return render_template('settings.html', settings=settings)

@settings_bp.route('', methods=['POST'])
@rate_limit(max_requests=30, time_window=60)  # 30 requests per minute
def save_settings():
    """Save user settings"""
    # Get form data
    settings_data = {
        'conversation_difficulty': request.form.get('conversation_difficulty', ConversationDifficulty.INTERMEDIATE.value),
        'enable_voice_responses': 'enable_voice_responses' in request.form,
        'preferred_language': request.form.get('preferred_language', 'en-US'),
        'theme': request.form.get('theme', 'light'),
        'color_theme': request.form.get('color_theme', 'default')
    }

    # Update settings for the current user or session
    try:
        settings_service.update_settings_for_user_or_session(session.get('user'), settings_data)
        flash('Settings saved successfully', 'success')
    except ValueError as e:
        flash(f'Error: {str(e)}', 'danger')
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'danger')

    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/reset', methods=['POST'])
def reset_settings():
    """Reset settings to defaults"""
    try:
        # Reset settings to defaults
        settings_service.reset_to_defaults(session.get('user', {}).get('id', 'demo_user'))
        flash('Settings reset to defaults', 'success')
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'danger')

    return redirect(url_for('settings.settings_page'))