"""
Alcoholics Anonymous recovery routes
All routes are prefixed with /aa
"""

import os
import json
import datetime
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app, abort, Response
from flask_login import login_required, current_user

# Import database from the app
from app import db

# Import AA recovery models from helper
from utils.aa_helper import (
    AASettings, AARecoveryLog, AAMeetingLog, AANightlyInventory,
    AASpotCheck, AASponsorCall, AAMindfulnessLog, AAAchievement
)
from utils.aa_helper import (
    find_meetings, log_meeting_attendance, get_daily_reflection, log_reflection_response,
    register_sponsor, log_sponsor_call, get_recovery_stats, set_sober_date, update_aa_settings,
    get_nightly_inventory_template, start_nightly_inventory, update_nightly_inventory, complete_nightly_inventory,
    get_random_spot_check, log_spot_check_response, get_crisis_resources, get_mindfulness_exercises,
    log_mindfulness_exercise, add_achievement
)

aa_bp = Blueprint('aa', __name__, url_prefix='/aa')

# Helper to get user_id from current_user
def get_user_id():
    return str(current_user.id) if current_user.is_authenticated else None

# Main AA dashboard
@aa_bp.route('/')
@login_required
def dashboard():
    """Main AA recovery dashboard"""
    user_id = get_user_id()
    
    # Get user settings
    settings = AASettings.query.filter_by(user_id=user_id).first()
    
    # Get recovery stats
    stats = get_recovery_stats(user_id)
    
    # Get daily reflection
    reflection = get_daily_reflection(user_id, "morning")
    
    # Check if we need to start/get nightly inventory
    now = datetime.now()
    inventory = None
    if now.hour >= 19:  # After 7 PM, show nightly inventory
        inventory_data = start_nightly_inventory(user_id)
        if "inventory" in inventory_data:
            inventory = inventory_data["inventory"]
            
    # Get recent spot checks
    recent_spot_checks = AASpotCheck.query.filter_by(user_id=user_id).order_by(
        AASpotCheck.timestamp.desc()).limit(5).all()
    
    # Check if pain flare monitoring is enabled
    pain_flare_enabled = False
    if settings:
        pain_flare_enabled = getattr(settings, 'track_pain_flares', False)
    
    return render_template('aa/dashboard.html',
                          settings=settings,
                          stats=stats,
                          reflection=reflection,
                          inventory=inventory,
                          recent_spot_checks=recent_spot_checks,
                          pain_flare_enabled=pain_flare_enabled)

# Settings routes
@aa_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """AA recovery settings page"""
    user_id = get_user_id()
    
    if request.method == 'POST':
        # Update settings
        settings_data = {}
        
        # Basic settings
        if 'sponsor_name' in request.form:
            settings_data['sponsor_name'] = request.form.get('sponsor_name')
        if 'sponsor_phone' in request.form:
            settings_data['sponsor_phone'] = request.form.get('sponsor_phone')
        if 'backup_contact_name' in request.form:
            settings_data['backup_contact_name'] = request.form.get('backup_contact_name')
        if 'backup_contact_phone' in request.form:
            settings_data['backup_contact_phone'] = request.form.get('backup_contact_phone')
        if 'home_group' in request.form:
            settings_data['home_group'] = request.form.get('home_group')
            
        # Sober date
        if 'sober_date' in request.form and request.form.get('sober_date'):
            try:
                sober_date = datetime.strptime(request.form.get('sober_date'), '%Y-%m-%d')
                settings_data['sober_date'] = sober_date
            except ValueError:
                flash('Invalid sober date format', 'error')
                
        # Display preferences
        if 'show_sober_days' in request.form:
            settings_data['show_sober_days'] = True
        else:
            settings_data['show_sober_days'] = False
            
        if 'track_honesty_streaks' in request.form:
            settings_data['track_honesty_streaks'] = True
        else:
            settings_data['track_honesty_streaks'] = False
            
        # Pain flare tracking (opt-in only)
        if 'track_pain_flares' in request.form:
            settings_data['track_pain_flares'] = True
        else:
            settings_data['track_pain_flares'] = False
            
        # Times
        if 'daily_reflection_time' in request.form:
            settings_data['daily_reflection_time'] = request.form.get('daily_reflection_time')
        if 'nightly_inventory_time' in request.form:
            settings_data['nightly_inventory_time'] = request.form.get('nightly_inventory_time')
        if 'spot_checks_per_day' in request.form:
            try:
                settings_data['spot_checks_per_day'] = int(request.form.get('spot_checks_per_day'))
            except (ValueError, TypeError):
                settings_data['spot_checks_per_day'] = 3  # Default
                
        # Update settings
        result = update_aa_settings(user_id, settings_data)
        
        if result.get('success'):
            flash('Settings updated successfully', 'success')
        else:
            flash(f'Error updating settings: {result.get("error")}', 'error')
            
        return redirect(url_for('aa_bp.settings'))
    
    # GET request - show settings form
    settings = AASettings.query.filter_by(user_id=user_id).first()
    
    return render_template('aa/settings.html', settings=settings)

# Meeting finder routes
@aa_bp.route('/meetings', methods=['GET', 'POST'])
@login_required
def meetings():
    """Find AA meetings"""
    user_id = get_user_id()
    meeting_results = None
    
    if request.method == 'POST':
        # Search for meetings
        zip_code = request.form.get('zip_code')
        radius = request.form.get('radius', 25)
        try:
            radius = int(radius)
        except (ValueError, TypeError):
            radius = 25
            
        day = request.form.get('day')
        if day:
            try:
                day = int(day)
            except (ValueError, TypeError):
                day = None
                
        time = request.form.get('time')
        types = request.form.getlist('types')
        
        # Find meetings
        meeting_results = find_meetings(zip_code, radius, day, time, types)
        
    return render_template('aa/meetings.html', meeting_results=meeting_results)

@aa_bp.route('/meetings/log', methods=['POST'])
@login_required
def log_meeting():
    """Log attendance at a meeting"""
    user_id = get_user_id()
    
    meeting_id = request.form.get('meeting_id')
    meeting_name = request.form.get('meeting_name')
    meeting_type = request.form.get('meeting_type', 'in_person')
    date_str = request.form.get('date_attended')
    
    try:
        date_attended = datetime.strptime(date_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        date_attended = datetime.now()
        
    pre_reflection = request.form.get('pre_reflection')
    reflection = request.form.get('reflection')
    honest_admit = request.form.get('honest_admit')
    
    result = log_meeting_attendance(
        user_id, meeting_id, meeting_name, meeting_type,
        date_attended, pre_reflection, reflection, honest_admit
    )
    
    if result.get('success'):
        flash('Meeting attendance logged successfully', 'success')
        
        # Check for new badges
        badges = result.get('new_badges', [])
        for badge in badges:
            if badge:
                flash(f'Achievement unlocked: {badge.get("badge_name")}!', 'success')
    else:
        flash(f'Error logging meeting: {result.get("error")}', 'error')
        
    return redirect(url_for('aa_bp.meetings'))

# Daily reflection routes
@aa_bp.route('/reflections/<reflection_type>')
@login_required
def reflections(reflection_type):
    """Get a daily reflection"""
    user_id = get_user_id()
    
    # Validate reflection type
    if reflection_type not in ['morning', 'evening']:
        reflection_type = 'morning'
        
    reflection = get_daily_reflection(user_id, reflection_type)
    
    return render_template('aa/reflection.html', 
                          reflection=reflection, 
                          reflection_type=reflection_type)

@aa_bp.route('/reflections/response', methods=['POST'])
@login_required
def reflection_response():
    """Log a response to a reflection"""
    user_id = get_user_id()
    
    reflection_content = request.form.get('reflection_content')
    response_content = request.form.get('response_content')
    is_honest_admit = 'is_honest_admit' in request.form
    
    result = log_reflection_response(
        user_id, reflection_content, response_content, is_honest_admit
    )
    
    if result.get('success'):
        flash('Response logged successfully', 'success')
        
        # Check for new badges
        badges = result.get('new_badges', [])
        for badge in badges:
            if badge:
                flash(f'Achievement unlocked: {badge.get("badge_name")}!', 'success')
    else:
        flash(f'Error logging response: {result.get("error")}', 'error')
        
    return redirect(url_for('aa_bp.dashboard'))

# Sponsor routes
@aa_bp.route('/sponsor', methods=['GET', 'POST'])
@login_required
def sponsor():
    """Sponsor contact page"""
    user_id = get_user_id()
    
    # Get settings
    settings = AASettings.query.filter_by(user_id=user_id).first()
    
    if request.method == 'POST':
        # Register sponsor
        sponsor_name = request.form.get('sponsor_name')
        sponsor_phone = request.form.get('sponsor_phone')
        backup_name = request.form.get('backup_name')
        backup_phone = request.form.get('backup_phone')
        
        result = register_sponsor(
            user_id, sponsor_name, sponsor_phone, backup_name, backup_phone
        )
        
        if result.get('success'):
            flash('Sponsor information updated successfully', 'success')
        else:
            flash(f'Error updating sponsor information: {result.get("error")}', 'error')
            
        return redirect(url_for('aa_bp.sponsor'))
    
    # Get recent calls
    recent_calls = AASponsorCall.query.filter_by(user_id=user_id).order_by(
        AASponsorCall.timestamp.desc()).limit(5).all()
    
    return render_template('aa/sponsor.html', 
                          settings=settings,
                          recent_calls=recent_calls)

@aa_bp.route('/sponsor/call', methods=['POST'])
@login_required
def sponsor_call():
    """Log a call to sponsor"""
    user_id = get_user_id()
    
    contact_type = request.form.get('contact_type', 'sponsor')
    pre_call_admission = request.form.get('pre_call_admission')
    post_call_admission = request.form.get('post_call_admission')
    
    result = log_sponsor_call(
        user_id, contact_type, pre_call_admission, post_call_admission
    )
    
    if result.get('success'):
        flash('Call logged successfully', 'success')
        
        # Check for new badges
        badges = result.get('new_badges', [])
        for badge in badges:
            if badge:
                flash(f'Achievement unlocked: {badge.get("badge_name")}!', 'success')
    else:
        flash(f'Error logging call: {result.get("error")}', 'error')
        
    return redirect(url_for('aa_bp.sponsor'))

# Stats routes
@aa_bp.route('/stats')
@login_required
def stats():
    """Recovery statistics page"""
    user_id = get_user_id()
    
    # Get stats
    stats = get_recovery_stats(user_id)
    
    return render_template('aa/stats.html', stats=stats)

@aa_bp.route('/stats/sober-date', methods=['POST'])
@login_required
def update_sober_date():
    """Update sober date"""
    user_id = get_user_id()
    
    sober_date_str = request.form.get('sober_date')
    
    try:
        sober_date = datetime.strptime(sober_date_str, '%Y-%m-%d')
    except (ValueError, TypeError):
        flash('Invalid date format', 'error')
        return redirect(url_for('aa_bp.stats'))
        
    result = set_sober_date(user_id, sober_date)
    
    if result.get('success'):
        flash('Sober date updated successfully', 'success')
        
        # Check for new badges
        badges = result.get('new_badges', [])
        for badge in badges:
            if badge:
                flash(f'Achievement unlocked: {badge.get("badge_name")}!', 'success')
    else:
        flash(f'Error updating sober date: {result.get("error")}', 'error')
        
    return redirect(url_for('aa_bp.stats'))

# Inventory routes
@aa_bp.route('/inventory/nightly', methods=['GET', 'POST'])
@login_required
def nightly_inventory():
    """Nightly inventory page"""
    user_id = get_user_id()
    
    if request.method == 'POST':
        # Complete or update inventory
        inventory_id = request.form.get('inventory_id')
        
        if 'complete' in request.form:
            # Complete the inventory
            result = complete_nightly_inventory(user_id, inventory_id)
            
            if result.get('success'):
                flash('Inventory completed successfully', 'success')
                
                # Check for new badges
                badges = result.get('new_badges', [])
                for badge in badges:
                    if badge:
                        flash(f'Achievement unlocked: {badge.get("badge_name")}!', 'success')
            else:
                flash(f'Error completing inventory: {result.get("error")}', 'error')
                
            return redirect(url_for('aa_bp.dashboard'))
        else:
            # Update inventory fields
            for field in request.form:
                if field in ['resentful', 'selfish', 'dishonest', 'afraid', 'secrets', 
                           'apologies_needed', 'gratitude', 'surrender', 
                           'wrong_actions', 'amends_owed', 'help_plan']:
                    update_nightly_inventory(user_id, inventory_id, field, request.form.get(field))
            
            flash('Inventory updated', 'success')
            
    # Start or get current inventory
    inventory_data = start_nightly_inventory(user_id)
    
    if 'error' in inventory_data:
        flash(f'Error loading inventory: {inventory_data.get("error")}', 'error')
        return redirect(url_for('aa_bp.dashboard'))
        
    inventory = inventory_data.get('inventory')
    template = inventory_data.get('template')
    
    return render_template('aa/nightly_inventory.html',
                          inventory=inventory,
                          template=template)

@aa_bp.route('/inventory/spot-check')
@login_required
def spot_check():
    """Spot-check inventory page"""
    user_id = get_user_id()
    
    # Get a random spot-check question
    category = request.args.get('category')
    spot_check = get_random_spot_check(user_id, category)
    
    return render_template('aa/spot_check.html', spot_check=spot_check)

@aa_bp.route('/inventory/spot-check/response', methods=['POST'])
@login_required
def spot_check_response():
    """Log a response to a spot-check question"""
    user_id = get_user_id()
    
    check_type = request.form.get('check_type')
    question = request.form.get('question')
    response = request.form.get('response')
    
    # Optional fields
    rating = None
    if 'rating' in request.form:
        try:
            rating = int(request.form.get('rating'))
        except (ValueError, TypeError):
            pass
            
    trigger = request.form.get('trigger')
    
    result = log_spot_check_response(
        user_id, check_type, question, response, rating, trigger
    )
    
    if result.get('success'):
        flash('Response logged successfully', 'success')
        
        # Check for new badges
        badges = result.get('new_badges', [])
        for badge in badges:
            if badge:
                flash(f'Achievement unlocked: {badge.get("badge_name")}!', 'success')
                
        # Check if this was an honest admission
        if result.get('is_honest_admit'):
            flash('Thank you for your honesty!', 'success')
    else:
        flash(f'Error logging response: {result.get("error")}', 'error')
        
    return redirect(url_for('aa_bp.dashboard'))

# Crisis resources
@aa_bp.route('/crisis')
def crisis():
    """Crisis resources page"""
    resources = get_crisis_resources()
    
    return render_template('aa/crisis.html', resources=resources)

# Mindfulness tools
@aa_bp.route('/mindfulness')
@login_required
def mindfulness():
    """Mindfulness tools page"""
    # Get all categories
    exercises = get_mindfulness_exercises()
    
    return render_template('aa/mindfulness.html', exercises=exercises)

@aa_bp.route('/mindfulness/<category>')
@login_required
def mindfulness_category(category):
    """Mindfulness tools for a specific category"""
    # Get exercises for this category
    exercises = get_mindfulness_exercises(category)
    
    if 'error' in exercises:
        flash(f'Error loading exercises: {exercises.get("error")}', 'error')
        return redirect(url_for('aa_bp.mindfulness'))
        
    return render_template('aa/mindfulness_category.html',
                          category=category,
                          exercises=exercises.get(category, []))

@aa_bp.route('/mindfulness/log', methods=['POST'])
@login_required
def log_mindfulness():
    """Log completion of a mindfulness exercise"""
    user_id = get_user_id()
    
    exercise_type = request.form.get('exercise_type')
    exercise_name = request.form.get('exercise_name')
    notes = request.form.get('notes')
    
    result = log_mindfulness_exercise(
        user_id, exercise_type, exercise_name, notes
    )
    
    if result.get('success'):
        flash('Exercise completion logged successfully', 'success')
        
        # Check for new badges
        badges = result.get('new_badges', [])
        for badge in badges:
            if badge:
                flash(f'Achievement unlocked: {badge.get("badge_name")}!', 'success')
    else:
        flash(f'Error logging exercise: {result.get("error")}', 'error')
        
    return redirect(url_for('aa_bp.mindfulness'))



# API for AJAX requests
@aa_bp.route('/api/spot-check/random')
@login_required
def api_random_spot_check():
    """API endpoint to get a random spot-check question"""
    user_id = get_user_id()
    
    category = request.args.get('category')
    spot_check = get_random_spot_check(user_id, category)
    
    return jsonify(spot_check)

@aa_bp.route('/api/reflection/random/<reflection_type>')
@login_required
def api_random_reflection(reflection_type):
    """API endpoint to get a random reflection"""
    user_id = get_user_id()
    
    # Validate reflection type
    if reflection_type not in ['morning', 'evening']:
        reflection_type = 'morning'
        
    reflection = get_daily_reflection(user_id, reflection_type)
    
    return jsonify(reflection)

# Pain flare monitoring (opt-in only)
@aa_bp.route('/pain-flares')
@login_required
def pain_flares():
    """Pain flare monitoring page (opt-in only)"""
    user_id = get_user_id()
    
    # Check if user is authorized to use this feature (only toldeonick98@gmail.com)
    from models import User
    user = User.query.get(user_id)
    if not user or user.email != "toldeonick98@gmail.com":
        flash("You are not authorized to use this feature.", "warning")
        return redirect(url_for('aa.dashboard'))
    
    # Check if pain flare monitoring is enabled
    settings = AASettings.query.filter_by(user_id=user_id).first()
    
    pain_flare_enabled = False
    if settings:
        pain_flare_enabled = getattr(settings, 'track_pain_flares', False)
        
    if not pain_flare_enabled:
        # Redirect to settings page with message
        flash('Pain flare monitoring is not enabled. Please enable it in settings if you wish to use this feature.', 'info')
        return redirect(url_for('aa_bp.settings'))
    
    # Get current weather data for pain flare prediction
    from utils.enhanced_weather_helper import get_weather_health_insights
    
    # Get primary location from settings
    location = "New York"  # Default
    if settings and settings.primary_location:
        location = settings.primary_location
        
    # Get pain flare insights with explicit opt-in flag
    health_insights = get_weather_health_insights(
        location=location,
        user_id=user_id,
        include_pain_flare_risk=True  # Explicitly request pain flare data
    )
    
    return render_template('aa/pain_flares.html',
                          health_insights=health_insights,
                          location=location)

@aa_bp.route('/api/toggle-pain-monitoring', methods=['POST'])
@login_required
def toggle_pain_monitoring():
    """API endpoint to toggle pain flare monitoring"""
    user_id = get_user_id()
    
    # Get current status from form
    enable = 'enable' in request.form
    
    # Update settings
    settings_data = {'track_pain_flares': enable}
    result = update_aa_settings(user_id, settings_data)
    
    if result.get('success'):
        status = "enabled" if enable else "disabled"
        flash(f'Pain flare monitoring {status} successfully', 'success')
    else:
        flash(f'Error updating settings: {result.get("error")}', 'error')
        
    return redirect(url_for('aa_bp.settings'))