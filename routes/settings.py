"""
Settings Routes Module

This module defines routes for the user settings and preferences.

@module routes.settings
@description User settings and preferences routes
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, UserSettings
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

# Create blueprint
settings_bp = Blueprint('settings', __name__)
logger = logging.getLogger(__name__)

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
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

def get_demo_user():
    """Get current user from session with demo fallback"""
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

@settings_bp.route('/settings')
def settings_page():
    """Render the settings page"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
    
    return render_template('settings.html')

@settings_bp.route('/settings/profile', methods=['POST'])
def update_profile():
    """Update user profile information"""
    try:
        user = session.get('user', {})
        # Update user information
        user['first_name'] = request.form.get('first_name', user.get('first_name'))
        user['last_name'] = request.form.get('last_name', user.get('last_name'))

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
        user = session.get('user', {})
        # Make sure user has settings
        if not user.get('settings'):
            user['settings'] = UserSettings(user_id=user.get('id', 'demo_user'))

        # Update settings
        user['settings'].theme = request.form.get('theme', 'light')

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
        user = session.get('user', {})
        # Make sure user has settings
        if not user.get('settings'):
            user['settings'] = UserSettings(user_id=user.get('id', 'demo_user'))

        # Update settings
        user['settings'].ai_name = request.form.get('ai_name', 'NOUS')
        user['settings'].ai_personality = request.form.get('ai_personality', 'helpful')
        user['settings'].preferred_language = request.form.get('preferred_language', 'en')
        user['settings'].enable_voice_responses = 'enable_voice' in request.form

        # Save changes
        db.session.commit()
        flash('Assistant preferences updated successfully!', 'success')

    except Exception as e:
        logger.error(f"Error updating assistant preferences: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating your assistant preferences.', 'danger')

    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/password', methods=['POST'])
def update_password():
    """Update user password"""
    try:
        # Check authentication
        auth_result = require_authentication()
        if auth_result:
            return auth_result
            
        user = session.get('user', {})
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

        # Check current password (simplified for demo)
        if not user.get('check_password', lambda x: True)(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('settings.settings_page'))

        # Update password (simplified for demo)
        if hasattr(user, 'set_password'):
            user.set_password(new_password)
        
        db.session.commit()
        flash('Password updated successfully!', 'success')

    except Exception as e:
        logger.error(f"Error updating password: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating your password.', 'danger')

    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/delete-account', methods=['POST'])
def delete_account():
    """Delete user account"""
    try:
        # Check authentication
        auth_result = require_authentication()
        if auth_result:
            return auth_result
            
        user = session.get('user', {})
        # Delete the user
        db.session.delete(user)
        db.session.commit()

        # Clear session
        session.clear()

        flash('Your account has been deleted.', 'info')
        return redirect(url_for('index.index'))

    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        db.session.rollback()
        flash('An error occurred while deleting your account.', 'danger')

    return redirect(url_for('settings.settings_page'))