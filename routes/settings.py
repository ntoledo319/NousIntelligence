"""

from utils.auth_compat import get_demo_user
def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, get_demo_user(), get_get_demo_user(), is_authenticated
    
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

def get_get_demo_user()():
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

Settings Routes Module

This module defines routes for the user settings and preferences.

@module routes.settings
@description User settings and preferences routes
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash

from models import db, UserSettings

# Create blueprint
settings_bp = Blueprint('settings', __name__)
logger = logging.getLogger(__name__)

@settings_bp.route('/settings')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def settings_page():
    """Render the settings page"""
    return render_template('settings.html')

@settings_bp.route('/settings/profile', methods=['POST'])
def update_profile():
    """Update user profile information"""
    try:
        # Update user information
        session.get('user', {}).get('first_name = request.form.get('first_name', session.get('user', {}).get('first_name)
        session.get('user', {}).get('last_name = request.form.get('last_name', session.get('user', {}).get('last_name)

        # Save changes
        db.session.commit()
        flash('Profile updated successfully!', 'success')

    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating your profile.', 'danger')

    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/appearance', methods=['POST'])
def update_appearance():
    """Update user appearance settings"""
    try:
        # Make sure user has settings
        if not session.get('user', {}).get('settings:
            session.get('user', {}).get('settings = UserSettings(user_id=session.get('user', {}).get('id', 'demo_user'))

        # Update settings
        session.get('user', {}).get('settings.theme = request.form.get('theme', 'light')

        # Save changes
        db.session.commit()
        flash('Appearance settings updated successfully!', 'success')

    except Exception as e:
        logger.error(f"Error updating appearance settings: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating your appearance settings.', 'danger')

    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/assistant', methods=['POST'])
def update_assistant():
    """Update assistant preferences"""
    try:
        # Make sure user has settings
        if not session.get('user', {}).get('settings:
            session.get('user', {}).get('settings = UserSettings(user_id=session.get('user', {}).get('id', 'demo_user'))

        # Update settings
        session.get('user', {}).get('settings.ai_name = request.form.get('ai_name', 'NOUS')
        session.get('user', {}).get('settings.ai_personality = request.form.get('ai_personality', 'helpful')
        session.get('user', {}).get('settings.preferred_language = request.form.get('preferred_language', 'en')
        session.get('user', {}).get('settings.enable_voice_responses = 'enable_voice' in request.form

        # Save changes
        db.session.commit()
        flash('Assistant preferences updated successfully!', 'success')

    except Exception as e:
        logger.error(f"Error updating assistant preferences: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating your assistant preferences.', 'danger')

    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/password', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def update_password():
    """Update user password"""
    try:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Validate inputs
        if not current_password or not new_password or not confirm_password:
            flash('All password fields are required.', 'warning')
            return redirect(url_for('settings.settings_page'))

        if new_password != confirm_password:
            flash('New passwords do not match.', 'warning')
            return redirect(url_for('settings.settings_page'))

        if not session.get('user', {}).get('check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('settings.settings_page'))

        # Update password
        session.get('user', {}).get('set_password(new_password)
        db.session.commit()
        flash('Password updated successfully!', 'success')

    except Exception as e:
        logger.error(f"Error updating password: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating your password.', 'danger')

    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/delete-account', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def delete_account():
    """Delete user account"""
    try:
        # Delete the user
        db.session.delete(session.get('user'))
        db.session.commit()

        # Log the user out
        
        logout_user()

        flash('Your account has been deleted.', 'info')
        return redirect(url_for('index.index'))

    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        db.session.rollback()
        flash('An error occurred while deleting your account.', 'danger')

    return redirect(url_for('settings.settings_page'))