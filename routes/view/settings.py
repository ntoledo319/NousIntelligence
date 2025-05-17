"""
Settings View Routes

This module contains view routes for the settings page.

@module routes.view.settings
@author NOUS Development Team
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_required
from models import ConversationDifficulty
from utils.security_helper import rate_limit
from services.settings import SettingsService

# Create blueprint
settings_bp = Blueprint('settings', __name__, url_prefix='/settings')

# Initialize service
settings_service = SettingsService()


@settings_bp.route('', methods=['GET'])
def settings_page():
    """Display user settings page"""
    # Get settings for the current user or session
    settings = settings_service.get_settings_for_user_or_session(current_user)
    
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
        settings_service.update_settings_for_user_or_session(current_user, settings_data)
        flash('Settings saved successfully', 'success')
    except ValueError as e:
        flash(f'Error: {str(e)}', 'danger')
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('settings.settings_page'))


@settings_bp.route('/reset', methods=['POST'])
@login_required
def reset_settings():
    """Reset settings to defaults"""
    try:
        # Reset settings to defaults
        settings_service.reset_to_defaults(current_user.id)
        flash('Settings reset to defaults', 'success')
    except Exception as e:
        flash(f'An unexpected error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('settings.settings_page')) 