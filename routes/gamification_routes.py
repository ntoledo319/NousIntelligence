"""
Gamification Routes

This module defines routes for gamification features including
achievements, points, streaks, challenges, and leaderboards.

@module routes.gamification_routes
@context_boundary Gamification System
"""

import logging
from flask import Blueprint, render_template, request, jsonify, session
from services.gamification_service import GamificationService
from utils.unified_auth import login_required, demo_allowed

logger = logging.getLogger(__name__)

# Create blueprint
gamification_bp = Blueprint('gamification', __name__, url_prefix='/gamification')

# Initialize service
gamification_service = GamificationService()

def get_current_user_id():
    """Get current user ID from session"""
    user = session.get('user', {})
    return user.get('id', 'demo_user')

# === Dashboard Routes ===

@gamification_bp.route('/')
@demo_allowed
def dashboard():
    """Gamification dashboard showing user's progress"""
    user_id = get_current_user_id()
    
    # Get user's gamification data
    points_summary = gamification_service.get_user_points_summary(user_id)
    achievements = gamification_service.get_user_achievements(user_id)
    streaks = gamification_service.get_all_user_streaks(user_id)
    
    # Get leaderboards
    weekly_leaderboard = gamification_service.get_leaderboard('weekly')
    monthly_leaderboard = gamification_service.get_leaderboard('monthly')
    
    # Get active challenges
    active_challenges = gamification_service.get_active_challenges()
    
    return render_template('gamification/dashboard.html',
                         points_summary=points_summary,
                         achievements=achievements,
                         streaks=streaks,
                         weekly_leaderboard=weekly_leaderboard,
                         monthly_leaderboard=monthly_leaderboard,
                         active_challenges=active_challenges)

# === Achievement Routes ===

@gamification_bp.route('/achievements')
@demo_allowed
def achievements_page():
    """View all achievements and progress"""
    user_id = get_current_user_id()
    
    # Get user's achievements
    earned_achievements = gamification_service.get_user_achievements(user_id)
    earned_ids = [a['id'] for a in earned_achievements]
    
    # Get all available achievements
    from models.gamification_models import Achievement
    all_achievements = Achievement.query.filter_by(is_active=True).all()
    
    # Categorize achievements
    achievements_by_category = {}
    for achievement in all_achievements:
        category = achievement.category
        if category not in achievements_by_category:
            achievements_by_category[category] = []
        
        achievement_dict = achievement.to_dict()
        achievement_dict['earned'] = achievement.id in earned_ids
        achievement_dict['earned_date'] = next(
            (a['earned_at'] for a in earned_achievements if a['id'] == achievement.id),
            None
        )
        achievements_by_category[category].append(achievement_dict)
    
    return render_template('gamification/achievements.html',
                         achievements_by_category=achievements_by_category,
                         total_earned=len(earned_achievements),
                         total_available=len(all_achievements))

@gamification_bp.route('/api/gamification/achievements')
@demo_allowed
def api_get_achievements():
    """API endpoint to get user's achievements"""
    user_id = get_current_user_id()
    
    achievements = gamification_service.get_user_achievements(user_id)
    
    return jsonify({
        'achievements': achievements,
        'total': len(achievements)
    })

# === Points Routes ===

@gamification_bp.route('/api/gamification/points')
@demo_allowed
def api_get_points():
    """API endpoint to get user's points summary"""
    user_id = get_current_user_id()
    
    points_summary = gamification_service.get_user_points_summary(user_id)
    
    return jsonify(points_summary)

@gamification_bp.route('/api/gamification/points/history')
@demo_allowed
def api_points_history():
    """API endpoint to get points transaction history"""
    user_id = get_current_user_id()
    limit = request.args.get('limit', 20, type=int)
    
    from models.gamification_models import PointTransaction
    transactions = PointTransaction.query.filter_by(user_id=user_id)\
                                       .order_by(PointTransaction.created_at.desc())\
                                       .limit(limit).all()
    
    history = [{
        'points': t.points,
        'type': t.transaction_type,
        'reason': t.reason,
        'category': t.category,
        'created_at': t.created_at.isoformat()
    } for t in transactions]
    
    return jsonify({
        'history': history,
        'count': len(history)
    })

# === Streak Routes ===

@gamification_bp.route('/streaks')
@demo_allowed
def streaks_page():
    """View all wellness streaks"""
    user_id = get_current_user_id()
    
    streaks = gamification_service.get_all_user_streaks(user_id)
    
    # Add friendly names for streak types
    streak_names = {
        'meditation': '🧘 Meditation',
        'mood_log': '📊 Mood Tracking',
        'exercise': '💪 Exercise',
        'journaling': '📝 Journaling',
        'dbt_skill': '🧠 DBT Skills',
        'cbt_exercise': '💭 CBT Exercises'
    }
    
    for streak in streaks:
        streak['friendly_name'] = streak_names.get(streak['streak_type'], streak['streak_type'])
    
    return render_template('gamification/streaks.html', streaks=streaks)

@gamification_bp.route('/api/gamification/streaks')
@demo_allowed
def api_get_streaks():
    """API endpoint to get user's streaks"""
    user_id = get_current_user_id()
    
    streaks = gamification_service.get_all_user_streaks(user_id)
    
    return jsonify({
        'streaks': streaks,
        'count': len(streaks)
    })

# === Leaderboard Routes ===

@gamification_bp.route('/leaderboard')
@demo_allowed
def leaderboard_page():
    """View leaderboards"""
    period = request.args.get('period', 'weekly')
    category = request.args.get('category', 'overall')
    
    leaderboard = gamification_service.get_leaderboard(period, category, limit=50)
    
    # Get user's rank
    user_id = get_current_user_id()
    user_rank = next((i + 1 for i, entry in enumerate(leaderboard) 
                     if entry['user_id'] == user_id), None)
    
    return render_template('gamification/leaderboard.html',
                         leaderboard=leaderboard,
                         period=period,
                         category=category,
                         user_rank=user_rank)

@gamification_bp.route('/api/gamification/leaderboard')
@demo_allowed
def api_get_leaderboard():
    """API endpoint to get leaderboard"""
    period = request.args.get('period', 'weekly')
    category = request.args.get('category', 'overall')
    limit = request.args.get('limit', 10, type=int)
    
    leaderboard = gamification_service.get_leaderboard(period, category, limit)
    
    return jsonify({
        'leaderboard': leaderboard,
        'period': period,
        'category': category
    })

# === Challenge Routes ===

@gamification_bp.route('/challenges')
@demo_allowed
def challenges_page():
    """View active challenges"""
    user_id = get_current_user_id()
    
    # Get active challenges
    active_challenges = gamification_service.get_active_challenges()
    
    # Get user's participation status for each challenge
    from models.gamification_models import ChallengeParticipation
    user_participations = ChallengeParticipation.query.filter_by(user_id=user_id).all()
    participation_map = {p.challenge_id: p for p in user_participations}
    
    challenges_data = []
    for challenge in active_challenges:
        challenge_dict = {
            'id': challenge.id,
            'name': challenge.name,
            'description': challenge.description,
            'category': challenge.category,
            'type': challenge.challenge_type,
            'points_reward': challenge.points_reward,
            'start_date': challenge.start_date.isoformat(),
            'end_date': challenge.end_date.isoformat(),
            'is_participating': challenge.id in participation_map,
            'progress': participation_map[challenge.id].progress if challenge.id in participation_map else 0
        }
        challenges_data.append(challenge_dict)
    
    return render_template('gamification/challenges.html',
                         challenges=challenges_data)

@gamification_bp.route('/api/gamification/challenges/<int:challenge_id>/join', methods=['POST'])
@login_required
def api_join_challenge(challenge_id):
    """API endpoint to join a challenge"""
    user_id = get_current_user_id()
    
    success = gamification_service.join_challenge(user_id, challenge_id)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Could not join challenge'}), 400

# === Utility Route ===

@gamification_bp.route('/api/gamification/trigger-achievement', methods=['POST'])
@login_required
def api_trigger_achievement_check():
    """API endpoint to manually trigger achievement check for an action"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    action_type = data.get('action_type')
    action_value = data.get('action_value', 1)
    
    if not action_type:
        return jsonify({'error': 'Action type required'}), 400
    
    earned = gamification_service.check_and_award_achievements(
        user_id, action_type, action_value
    )
    
    return jsonify({
        'earned_achievements': [a.to_dict() for a in earned],
        'count': len(earned)
    })


# AI-GENERATED [2024-12-01]
# TRAINING_DATA: Gamification patterns from Duolingo, Habitica
# @see services.gamification_service for business logic 