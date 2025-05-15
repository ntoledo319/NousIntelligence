"""
Alcoholics Anonymous Recovery Routes
Provides API endpoints for AA recovery features
"""

import os
import json
from flask import Blueprint, request, jsonify, session, current_app
from datetime import datetime, timedelta
from functools import wraps
from flask_login import login_required, current_user

from utils.aa_helper import (
    get_user_settings, update_user_settings, get_daily_reflection,
    get_evening_prompts, log_recovery_entry, get_recovery_logs,
    search_meetings, log_meeting_attendance, get_attended_meetings,
    create_nightly_inventory, get_nightly_inventories, get_random_spot_check,
    log_spot_check, get_spot_checks, log_sponsor_call, get_sponsor_calls,
    get_mindfulness_exercises, log_mindfulness_exercise, get_recovery_stats,
    create_forum_post, get_forum_posts, get_crisis_resources
)

aa_bp = Blueprint('aa', __name__, url_prefix='/api/aa')

# Helper function to get the current user ID
def get_current_user_id():
    """Get the current user ID from Flask-Login or session"""
    if current_user and current_user.is_authenticated:
        return current_user.id
    # Fallback to session if Flask-Login not available
    if 'user_id' in session:
        return session['user_id']
    return None

# User settings routes

@aa_bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    """Get AA settings for the current user"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    settings = get_user_settings(user_id)
    return jsonify(settings)

@aa_bp.route('/settings', methods=['POST'])
@login_required
def update_settings():
    """Update AA settings for the current user"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    settings_data = request.json
    result = update_user_settings(user_id, settings_data)
    return jsonify(result)

# Daily reflection routes

@aa_bp.route('/reflection/daily', methods=['GET'])
def get_reflection():
    """Get a daily reflection"""
    reflection = get_daily_reflection()
    return jsonify(reflection)

@aa_bp.route('/reflection/log', methods=['POST'])
@login_required
def log_reflection():
    """Log a reflection response"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    data = request.json
    content = data.get('content', '')
    is_honest_admit = data.get('is_honest_admit', False)
    
    result = log_recovery_entry(
        user_id=user_id,
        log_type='reflection',
        content=content,
        is_honest_admit=is_honest_admit
    )
    
    return jsonify(result)

# Inventory routes

@aa_bp.route('/inventory/evening-prompts', methods=['GET'])
def get_evening_inventory_prompts():
    """Get evening inventory prompts"""
    prompts = get_evening_prompts()
    return jsonify(prompts)

@aa_bp.route('/inventory/nightly', methods=['POST'])
@login_required
def create_inventory():
    """Create a nightly inventory entry"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    inventory_data = request.json
    result = create_nightly_inventory(user_id, inventory_data)
    return jsonify(result)

@aa_bp.route('/inventory/nightly', methods=['GET'])
@login_required
def get_inventories():
    """Get nightly inventories for the current user"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    # Get optional limit parameter
    limit = request.args.get('limit', default=7, type=int)
    
    result = get_nightly_inventories(user_id, limit)
    return jsonify(result)

# Spot-check routes

@aa_bp.route('/spot-check', methods=['GET'])
def get_spot_check():
    """Get a random spot-check question"""
    check = get_random_spot_check()
    return jsonify(check)

@aa_bp.route('/spot-check', methods=['POST'])
@login_required
def create_spot_check():
    """Log a spot-check response"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    check_data = request.json
    result = log_spot_check(user_id, check_data)
    return jsonify(result)

@aa_bp.route('/spot-check/history', methods=['GET'])
@login_required
def get_spot_check_history():
    """Get spot-check history for the current user"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    # Get optional parameters
    check_type = request.args.get('type')
    limit = request.args.get('limit', default=20, type=int)
    
    result = get_spot_checks(user_id, check_type, limit)
    return jsonify(result)

# Meeting routes

@aa_bp.route('/meetings/search', methods=['GET'])
def search_aa_meetings():
    """Search for AA meetings"""
    location = request.args.get('location', '')
    day = request.args.get('day')
    time = request.args.get('time')
    
    result = search_meetings(location, day, time)
    return jsonify(result)

@aa_bp.route('/meetings', methods=['POST'])
@login_required
def log_meeting():
    """Log a meeting attendance"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    meeting_data = request.json
    result = log_meeting_attendance(user_id, meeting_data)
    return jsonify(result)

@aa_bp.route('/meetings', methods=['GET'])
@login_required
def get_meetings():
    """Get meetings attended by the current user"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    # Get optional limit parameter
    limit = request.args.get('limit', default=20, type=int)
    
    result = get_attended_meetings(user_id, limit)
    return jsonify(result)

# Sponsor call routes

@aa_bp.route('/sponsor/call', methods=['POST'])
@login_required
def log_call():
    """Log a call to sponsor or backup contact"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    call_data = request.json
    result = log_sponsor_call(user_id, call_data)
    return jsonify(result)

@aa_bp.route('/sponsor/calls', methods=['GET'])
@login_required
def get_calls():
    """Get sponsor calls for the current user"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    # Get optional limit parameter
    limit = request.args.get('limit', default=10, type=int)
    
    result = get_sponsor_calls(user_id, limit)
    return jsonify(result)

# Mindfulness routes

@aa_bp.route('/mindfulness', methods=['GET'])
def get_mindfulness():
    """Get mindfulness exercises"""
    exercise_type = request.args.get('type')
    result = get_mindfulness_exercises(exercise_type)
    return jsonify(result)

@aa_bp.route('/mindfulness/log', methods=['POST'])
@login_required
def log_mindfulness():
    """Log a mindfulness exercise usage"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    exercise_data = request.json
    result = log_mindfulness_exercise(user_id, exercise_data)
    return jsonify(result)

# Stats and achievements routes

@aa_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """Get recovery statistics for the current user"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    result = get_recovery_stats(user_id)
    return jsonify(result)

# Forum routes

@aa_bp.route('/forum/posts', methods=['GET'])
def get_posts():
    """Get forum posts"""
    parent_id = request.args.get('parent_id', type=int)
    include_replies = request.args.get('include_replies', default='true').lower() == 'true'
    limit = request.args.get('limit', default=20, type=int)
    
    result = get_forum_posts(parent_id, include_replies, limit)
    return jsonify(result)

@aa_bp.route('/forum/posts', methods=['POST'])
@login_required
def create_post():
    """Create a forum post"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    post_data = request.json
    result = create_forum_post(user_id, post_data)
    return jsonify(result)

# Crisis resources route

@aa_bp.route('/crisis/resources', methods=['GET'])
def get_crisis_help():
    """Get crisis resources and helplines"""
    resources = get_crisis_resources()
    return jsonify(resources)

# Recovery log routes

@aa_bp.route('/logs', methods=['GET'])
@login_required
def get_logs():
    """Get recovery logs for the current user"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    # Get optional parameters
    log_type = request.args.get('type')
    limit = request.args.get('limit', default=20, type=int)
    
    # Parse date parameters if provided
    start_date = None
    if 'start_date' in request.args:
        try:
            start_date = datetime.fromisoformat(request.args.get('start_date').replace('Z', '+00:00'))
        except ValueError:
            pass
            
    end_date = None
    if 'end_date' in request.args:
        try:
            end_date = datetime.fromisoformat(request.args.get('end_date').replace('Z', '+00:00'))
        except ValueError:
            pass
    
    result = get_recovery_logs(user_id, log_type, start_date, end_date, limit)
    return jsonify(result)

@aa_bp.route('/logs', methods=['POST'])
@login_required
def create_log():
    """Create a recovery log entry"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401
    
    data = request.json
    log_type = data.get('log_type', 'general')
    content = data.get('content', '')
    category = data.get('category')
    is_honest_admit = data.get('is_honest_admit', False)
    
    result = log_recovery_entry(
        user_id=user_id,
        log_type=log_type,
        content=content,
        category=category,
        is_honest_admit=is_honest_admit
    )
    
    return jsonify(result)