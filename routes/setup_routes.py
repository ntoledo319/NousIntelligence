"""
Setup wizard routes
All routes are prefixed with /setup
"""

import os
import json
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user

# Import database models
from app import db
from models import AssistantProfile, UserSettings

# Import setup wizard helpers
from utils.setup_wizard import (
    get_assistant_profile, customize_assistant, 
    get_setup_progress, update_setup_progress,
    get_personality_options, delete_customization,
    initialize_user_settings
)

setup_bp = Blueprint('setup', __name__, url_prefix='/setup')

# Helper to get user_id from current_user
def get_user_id():
    return str(current_user.id) if current_user.is_authenticated else None

# Setup wizard main page
@setup_bp.route('/')
def wizard():
    """Setup wizard main page - redirects to appropriate step"""
    user_id = get_user_id() if current_user.is_authenticated else None
    
    # Get current setup progress
    progress = get_setup_progress(user_id) if user_id else {'has_completed_setup': False, 'next_step': 'welcome'}
    
    # If setup is complete, redirect to dashboard
    if progress.get('has_completed_setup', False) and not request.args.get('restart'):
        return redirect(url_for('index'))
    
    # Otherwise redirect to next step
    next_step = progress.get('next_step', 'welcome') or 'welcome'
    return redirect(url_for(f'setup.{next_step}'))

# Welcome step
@setup_bp.route('/welcome')
def welcome():
    """Welcome step of setup wizard"""
    user_id = get_user_id() if current_user.is_authenticated else None
    
    # Get current setup progress
    progress = get_setup_progress(user_id) if user_id else {}
    
    return render_template(
        'setup/welcome.html',
        progress=progress,
        user=current_user
    )

# Complete welcome step
@setup_bp.route('/welcome/complete', methods=['POST'])
@login_required
def welcome_complete():
    """Complete welcome step"""
    user_id = get_user_id()
    
    # Update setup progress
    update_setup_progress(user_id, 'welcome')
    
    return redirect(url_for('setup.personalize'))

# Personalize assistant step
@setup_bp.route('/personalize')
@login_required
def personalize():
    """Personalize assistant step of setup wizard"""
    user_id = get_user_id()
    
    # Get current setup progress
    progress = get_setup_progress(user_id)
    
    # Get current assistant profile
    profile = get_assistant_profile(user_id)
    
    # Get personality options
    personality_options = get_personality_options()
    
    return render_template(
        'setup/personalize.html',
        progress=progress,
        profile=profile,
        personality_options=personality_options,
        user=current_user
    )

# Save assistant personalization
@setup_bp.route('/personalize/save', methods=['POST'])
@login_required
def personalize_save():
    """Save assistant personalization"""
    user_id = get_user_id()
    
    # Get form data
    data = {
        'name': request.form.get('assistant_name'),
        'display_name': request.form.get('display_name'),
        'tagline': request.form.get('tagline'),
        'description': request.form.get('description'),
        'primary_color': request.form.get('primary_color'),
        'theme': request.form.get('theme'),
        'personality': request.form.get('personality')
    }
    
    # Handle logo upload if present
    if 'logo' in request.files and request.files['logo'].filename:
        # Read file and convert to base64
        import base64
        logo_file = request.files['logo']
        logo_data = logo_file.read()
        data['logo_data'] = f"data:image/png;base64,{base64.b64encode(logo_data).decode('utf-8')}"
    
    # Update assistant profile
    customize_assistant(user_id, data)
    
    # Update setup progress
    update_setup_progress(user_id, 'personalize')
    
    return redirect(url_for('setup.preferences'))

# Preferences step
@setup_bp.route('/preferences')
@login_required
def preferences():
    """User preferences step of setup wizard"""
    user_id = get_user_id()
    
    # Get current setup progress
    progress = get_setup_progress(user_id)
    
    # Get or initialize user settings
    settings = initialize_user_settings(user_id)
    
    return render_template(
        'setup/preferences.html',
        progress=progress,
        settings=settings,
        user=current_user
    )

# Save user preferences
@setup_bp.route('/preferences/save', methods=['POST'])
@login_required
def preferences_save():
    """Save user preferences"""
    user_id = get_user_id()
    
    # Get or initialize user settings
    settings = initialize_user_settings(user_id)
    
    # Check if settings were successfully created/retrieved
    if not settings:
        flash("Error retrieving user settings. Please try again.", "error")
        return redirect(url_for('setup.preferences'))
    
    # Update settings from form
    settings.theme = request.form.get('theme', 'dark')
    settings.preferred_language = request.form.get('language', 'en-US')
    settings.conversation_difficulty = request.form.get('difficulty', 'intermediate')
    settings.enable_voice_responses = request.form.get('enable_voice') == 'on'
    
    # Update AI personality settings
    settings.ai_name = request.form.get('ai_name', 'NOUS')
    settings.ai_personality = request.form.get('ai_personality', 'helpful')
    settings.ai_formality = request.form.get('ai_formality', 'casual')
    settings.ai_verbosity = request.form.get('ai_verbosity', 'balanced')
    settings.ai_enthusiasm = request.form.get('ai_enthusiasm', 'moderate')
    settings.ai_emoji_usage = request.form.get('ai_emoji_usage', 'occasional')
    
    db.session.commit()
    
    # Update setup progress
    update_setup_progress(user_id, 'preferences')
    
    return redirect(url_for('setup.features'))

# Features step
@setup_bp.route('/features')
@login_required
def features():
    """Enable/disable features step of setup wizard"""
    user_id = get_user_id()
    
    # Get current setup progress
    progress = get_setup_progress(user_id)
    
    # Get or initialize user settings
    settings = initialize_user_settings(user_id)
    
    return render_template(
        'setup/features.html',
        progress=progress,
        settings=settings,
        user=current_user
    )

# Save features preferences
@setup_bp.route('/features/save', methods=['POST'])
@login_required
def features_save():
    """Save features preferences"""
    user_id = get_user_id()
    
    # Get or initialize user settings
    settings = initialize_user_settings(user_id)
    
    # Check if settings were successfully created/retrieved
    if not settings:
        flash("Error retrieving user settings. Please try again.", "error")
        return redirect(url_for('setup.features'))
    
    # Update notification settings
    settings.email_notifications = request.form.get('email_notifications') == 'on'
    settings.push_notifications = request.form.get('push_notifications') == 'on'
    
    # Update budget settings
    settings.budget_reminder_enabled = request.form.get('budget_reminders') == 'on'
    
    db.session.commit()
    
    # Update setup progress
    update_setup_progress(user_id, 'features')
    
    return redirect(url_for('setup.complete'))

# Complete setup step
@setup_bp.route('/complete')
@login_required
def complete():
    """Complete setup step of wizard"""
    user_id = get_user_id()
    
    # Get current setup progress
    progress = get_setup_progress(user_id)
    
    # Get or initialize user settings
    settings = initialize_user_settings(user_id)
    
    # Get assistant profile
    profile = get_assistant_profile(user_id)
    
    return render_template(
        'setup/complete.html',
        progress=progress,
        profile=profile,
        settings=settings, 
        user=current_user
    )

# Finalize setup
@setup_bp.route('/finalize', methods=['POST'])
@login_required
def finalize():
    """Finalize setup and mark as complete"""
    user_id = get_user_id()
    
    # Mark setup as completed
    update_setup_progress(user_id, 'complete', setup_completed=True)
    
    # Redirect to dashboard
    flash(f"Setup complete! Welcome to your personalized assistant.", "success")
    return redirect(url_for('index'))

# Reset setup wizard
@setup_bp.route('/reset', methods=['POST'])
@login_required
def reset():
    """Reset setup wizard and start over"""
    user_id = get_user_id()
    
    # Get current user settings
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    
    if settings and settings.setup_progress:
        # Clear setup progress
        settings.setup_progress = None
        db.session.commit()
    
    # Delete custom assistant profile
    delete_customization(user_id)
    
    flash("Setup wizard has been reset.", "info")
    return redirect(url_for('setup.wizard'))