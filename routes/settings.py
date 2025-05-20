"""
Settings Routes Module

This module defines routes for the user settings and preferences.

@module routes.settings
@description User settings and preferences routes
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, UserSettings

# Create blueprint
settings_bp = Blueprint('settings', __name__)
logger = logging.getLogger(__name__)

@settings_bp.route('/settings')
@login_required
def settings_page():
    """Render the settings page"""
    return render_template('settings.html')

@settings_bp.route('/settings/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    try:
        # Update user information
        current_user.first_name = request.form.get('first_name', current_user.first_name)
        current_user.last_name = request.form.get('last_name', current_user.last_name)
        
        # Save changes
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating your profile.', 'danger')
        
    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/appearance', methods=['POST'])
@login_required
def update_appearance():
    """Update user appearance settings"""
    try:
        # Make sure user has settings
        if not current_user.settings:
            current_user.settings = UserSettings(user_id=current_user.id)
            
        # Update settings
        current_user.settings.theme = request.form.get('theme', 'light')
        
        # Save changes
        db.session.commit()
        flash('Appearance settings updated successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error updating appearance settings: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating your appearance settings.', 'danger')
        
    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/assistant', methods=['POST'])
@login_required
def update_assistant():
    """Update assistant preferences"""
    try:
        # Make sure user has settings
        if not current_user.settings:
            current_user.settings = UserSettings(user_id=current_user.id)
            
        # Update settings
        current_user.settings.ai_name = request.form.get('ai_name', 'NOUS')
        current_user.settings.ai_personality = request.form.get('ai_personality', 'helpful')
        current_user.settings.preferred_language = request.form.get('preferred_language', 'en')
        current_user.settings.enable_voice_responses = 'enable_voice' in request.form
        
        # Save changes
        db.session.commit()
        flash('Assistant preferences updated successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error updating assistant preferences: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating your assistant preferences.', 'danger')
        
    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/password', methods=['POST'])
@login_required
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
            
        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('settings.settings_page'))
            
        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password updated successfully!', 'success')
        
    except Exception as e:
        logger.error(f"Error updating password: {str(e)}")
        db.session.rollback()
        flash('An error occurred while updating your password.', 'danger')
        
    return redirect(url_for('settings.settings_page'))

@settings_bp.route('/settings/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account"""
    try:
        # Delete the user
        db.session.delete(current_user)
        db.session.commit()
        
        # Log the user out
        from flask_login import logout_user
        logout_user()
        
        flash('Your account has been deleted.', 'info')
        return redirect(url_for('index.index'))
        
    except Exception as e:
        logger.error(f"Error deleting account: {str(e)}")
        db.session.rollback()
        flash('An error occurred while deleting your account.', 'danger')
        
    return redirect(url_for('settings.settings_page')) 