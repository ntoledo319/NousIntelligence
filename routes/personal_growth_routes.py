"""
Personal Growth Routes

This module defines routes for personal development features including
goal setting, habit tracking, journaling, and vision boards.

@module routes.personal_growth_routes
@context_boundary Personal Development
"""

import logging
from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from services.personal_growth_service import PersonalGrowthService
from utils.unified_auth import login_required, demo_allowed

logger = logging.getLogger(__name__)

# Create blueprint
growth_bp = Blueprint('growth', __name__, url_prefix='/growth')

# Initialize service
growth_service = PersonalGrowthService()

def get_current_user_id():
    """Get current user ID from session"""
    user = session.get('user', {})
    return user.get('id', 'demo_user')

# === Dashboard Route ===

@growth_bp.route('/')
@demo_allowed
def dashboard():
    """Personal growth dashboard"""
    user_id = get_current_user_id()
    
    # Get growth statistics
    stats = growth_service.get_personal_growth_stats(user_id)
    
    # Get recent data
    recent_goals = growth_service.get_user_goals(user_id, status='active')[:3]
    recent_journal = growth_service.get_journal_entries(user_id, limit=3)
    
    return render_template('growth/dashboard.html',
                         stats=stats,
                         recent_goals=recent_goals,
                         recent_journal=recent_journal)

# === Goal Routes ===

@growth_bp.route('/goals')
@demo_allowed
def goals_index():
    """Goals overview page"""
    user_id = get_current_user_id()
    status = request.args.get('status')
    category = request.args.get('category')
    
    goals = growth_service.get_user_goals(user_id, status, category)
    
    # Categorize goals
    active_goals = [g for g in goals if g.status == 'active']
    completed_goals = [g for g in goals if g.status == 'completed']
    
    return render_template('growth/goals.html',
                         active_goals=active_goals,
                         completed_goals=completed_goals,
                         total_goals=len(goals))

@growth_bp.route('/goals/new')
@login_required
def new_goal():
    """Create new goal page"""
    categories = ['health', 'career', 'personal', 'financial', 'social', 'education']
    goal_types = ['daily', 'weekly', 'monthly', 'yearly', 'long_term']
    
    return render_template('growth/new_goal.html',
                         categories=categories,
                         goal_types=goal_types)

@growth_bp.route('/api/growth/goals', methods=['POST'])
@login_required
def api_create_goal():
    """API endpoint to create a goal"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    title = data.get('title')
    description = data.get('description')
    category = data.get('category')
    goal_type = data.get('goal_type', 'long_term')
    time_bound = data.get('time_bound')
    
    # SMART goal components
    specific = data.get('specific')
    measurable = data.get('measurable')
    achievable = data.get('achievable')
    relevant = data.get('relevant')
    
    if not title or not category:
        return jsonify({'error': 'Title and category required'}), 400
    
    # Convert time_bound string to date if provided
    time_bound_date = None
    if time_bound:
        try:
            time_bound_date = datetime.fromisoformat(time_bound).date()
        except:
            pass
    
    goal = growth_service.create_goal(
        user_id, title, description, category, goal_type, time_bound_date
    )
    
    if goal:
        # Update SMART components
        goal.specific = specific
        goal.measurable = measurable
        goal.achievable = achievable
        goal.relevant = relevant
        from database import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'goal': goal.to_dict()
        })
    else:
        return jsonify({'error': 'Could not create goal'}), 500

@growth_bp.route('/api/growth/goals/<int:goal_id>/progress', methods=['PUT'])
@login_required
def api_update_goal_progress(goal_id):
    """API endpoint to update goal progress"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    progress = data.get('progress', 0)
    
    success = growth_service.update_goal_progress(user_id, goal_id, progress)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Could not update progress'}), 400

# === Habit Routes ===

@growth_bp.route('/habits')
@demo_allowed
def habits_index():
    """Habits tracking page"""
    user_id = get_current_user_id()
    
    from models.personal_growth_models import Habit, HabitEntry
    habits = Habit.query.filter_by(user_id=user_id, is_active=True).all()
    
    # Get today's entries
    today = date.today()
    today_entries = {}
    for habit in habits:
        entry = HabitEntry.query.filter_by(
            habit_id=habit.id,
            entry_date=today
        ).first()
        today_entries[habit.id] = entry
    
    return render_template('growth/habits.html',
                         habits=habits,
                         today_entries=today_entries,
                         today=today)

@growth_bp.route('/habits/new')
@login_required
def new_habit():
    """Create new habit page"""
    categories = ['health', 'productivity', 'mindfulness', 'learning', 'social']
    
    return render_template('growth/new_habit.html',
                         categories=categories)

@growth_bp.route('/api/growth/habits', methods=['POST'])
@login_required
def api_create_habit():
    """API endpoint to create a habit"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    name = data.get('name')
    description = data.get('description')
    category = data.get('category')
    habit_type = data.get('habit_type', 'daily')
    frequency_days = data.get('frequency_days')
    reminder_time = data.get('reminder_time')
    
    if not name or not category:
        return jsonify({'error': 'Name and category required'}), 400
    
    # Convert reminder time string to time object
    reminder_time_obj = None
    if reminder_time:
        try:
            reminder_time_obj = datetime.strptime(reminder_time, '%H:%M').time()
        except:
            pass
    
    habit = growth_service.create_habit(
        user_id, name, description, category, habit_type,
        frequency_days, reminder_time_obj
    )
    
    if habit:
        return jsonify({
            'success': True,
            'habit_id': habit.id
        })
    else:
        return jsonify({'error': 'Could not create habit'}), 500

@growth_bp.route('/api/growth/habits/<int:habit_id>/log', methods=['POST'])
@login_required
def api_log_habit(habit_id):
    """API endpoint to log habit completion"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    completed = data.get('completed', True)
    value = data.get('value')
    notes = data.get('notes')
    
    success = growth_service.log_habit_completion(
        user_id, habit_id, completed, value, notes
    )
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Could not log habit'}), 400

@growth_bp.route('/api/growth/habits/<int:habit_id>/stats')
@demo_allowed
def api_habit_stats(habit_id):
    """API endpoint to get habit statistics"""
    user_id = get_current_user_id()
    days = request.args.get('days', 30, type=int)
    
    stats = growth_service.get_habit_stats(user_id, habit_id, days)
    
    return jsonify(stats)

# === Journal Routes ===

@growth_bp.route('/journal')
@demo_allowed
def journal_index():
    """Journal/diary main page"""
    user_id = get_current_user_id()
    entry_type = request.args.get('type')
    
    entries = growth_service.get_journal_entries(user_id, entry_type, limit=20)
    
    # Get a reflection prompt
    prompt = growth_service.get_random_reflection_prompt()
    
    return render_template('growth/journal.html',
                         entries=entries,
                         reflection_prompt=prompt)

@growth_bp.route('/journal/new')
@login_required
def new_journal_entry():
    """Create new journal entry page"""
    # Get a reflection prompt
    prompt = growth_service.get_random_reflection_prompt()
    
    entry_types = ['general', 'gratitude', 'reflection', 'dream', 'goals']
    
    return render_template('growth/new_journal_entry.html',
                         prompt=prompt,
                         entry_types=entry_types)

@growth_bp.route('/api/growth/journal', methods=['POST'])
@login_required
def api_create_journal_entry():
    """API endpoint to create journal entry"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    content = data.get('content')
    title = data.get('title')
    entry_type = data.get('entry_type', 'general')
    mood_rating = data.get('mood_rating')
    emotions = data.get('emotions', [])
    tags = data.get('tags', [])
    
    if not content:
        return jsonify({'error': 'Content required'}), 400
    
    entry = growth_service.create_journal_entry(
        user_id, content, title, entry_type,
        mood_rating, emotions, tags
    )
    
    if entry:
        return jsonify({
            'success': True,
            'entry_id': entry.id
        })
    else:
        return jsonify({'error': 'Could not create entry'}), 500

@growth_bp.route('/api/growth/journal/prompts')
@demo_allowed
def api_get_prompt():
    """API endpoint to get a reflection prompt"""
    category = request.args.get('category')
    
    prompt = growth_service.get_random_reflection_prompt(category)
    
    if prompt:
        return jsonify({
            'prompt': prompt.prompt_text,
            'category': prompt.category,
            'difficulty': prompt.difficulty_level
        })
    else:
        return jsonify({'error': 'No prompts available'}), 404

# === Vision Board Routes ===

@growth_bp.route('/vision-boards')
@demo_allowed
def vision_boards_index():
    """Vision boards overview"""
    user_id = get_current_user_id()
    
    from models.personal_growth_models import VisionBoard
    boards = VisionBoard.query.filter_by(user_id=user_id).all()
    
    return render_template('growth/vision_boards.html',
                         boards=boards)

@growth_bp.route('/vision-boards/new')
@login_required
def new_vision_board():
    """Create new vision board page"""
    themes = ['career', 'health', 'relationships', 'personal', 'travel', 'lifestyle']
    
    return render_template('growth/new_vision_board.html',
                         themes=themes)

@growth_bp.route('/api/growth/vision-boards', methods=['POST'])
@login_required
def api_create_vision_board():
    """API endpoint to create vision board"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    title = data.get('title')
    description = data.get('description')
    theme = data.get('theme')
    is_public = data.get('is_public', False)
    
    if not title or not theme:
        return jsonify({'error': 'Title and theme required'}), 400
    
    board = growth_service.create_vision_board(
        user_id, title, description, theme, is_public
    )
    
    if board:
        return jsonify({
            'success': True,
            'board_id': board.id
        })
    else:
        return jsonify({'error': 'Could not create board'}), 500

@growth_bp.route('/api/growth/vision-boards/<int:board_id>/items', methods=['POST'])
@login_required
def api_add_vision_board_item(board_id):
    """API endpoint to add item to vision board"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    item_type = data.get('item_type')
    content = data.get('content')
    caption = data.get('caption')
    position_x = data.get('position_x', 0)
    position_y = data.get('position_y', 0)
    linked_goal_id = data.get('linked_goal_id')
    
    if not item_type or not content:
        return jsonify({'error': 'Type and content required'}), 400
    
    item = growth_service.add_vision_board_item(
        user_id, board_id, item_type, content, caption,
        position_x, position_y, linked_goal_id
    )
    
    if item:
        return jsonify({
            'success': True,
            'item_id': item.id
        })
    else:
        return jsonify({'error': 'Could not add item'}), 500

# === Stats Route ===

@growth_bp.route('/api/growth/stats')
@demo_allowed
def api_growth_stats():
    """API endpoint to get personal growth statistics"""
    user_id = get_current_user_id()
    
    stats = growth_service.get_personal_growth_stats(user_id)
    
    return jsonify(stats)


# AI-GENERATED [2024-12-01]
# ## Affected Components: templates/growth/*, services.personal_growth_service
# ORIGINAL_INTENT: Empower users with tools for personal development 