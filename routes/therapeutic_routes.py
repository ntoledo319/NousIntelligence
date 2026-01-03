"""
Therapeutic Routes - CBT, DBT, AA Features
Consolidated therapeutic endpoints
"""
from flask import Blueprint, request, jsonify, session
from functools import wraps
from datetime import datetime
import logging

from repositories.therapeutic_repository import TherapeuticRepository
from utils.unified_auth import demo_allowed, get_current_user_id

logger = logging.getLogger(__name__)

therapeutic_bp = Blueprint('therapeutic', __name__, url_prefix='/api/v1/therapeutic')

# ===== DBT SKILL LOGS =====

@therapeutic_bp.route('/dbt/skills/log', methods=['POST'])
@demo_allowed
def log_dbt_skill():
    """Log usage of a DBT skill"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or 'skill_name' not in data or 'category' not in data:
        return jsonify({'error': 'skill_name and category required'}), 400
    
    skill_log = TherapeuticRepository.create_skill_log(
        user_id=user_id,
        skill_name=data['skill_name'],
        category=data['category'],
        situation=data.get('situation', ''),
        effectiveness=data.get('effectiveness', 5),
        notes=data.get('notes', '')
    )
    
    if skill_log:
        return jsonify(skill_log.to_dict()), 201
    return jsonify({'error': 'Failed to log skill'}), 500

@therapeutic_bp.route('/dbt/skills/logs', methods=['GET'])
@demo_allowed
def get_skill_logs():
    """Get recent skill logs for user"""
    user_id = get_current_user_id()
    limit = request.args.get('limit', 50, type=int)
    
    logs = TherapeuticRepository.get_user_skill_logs(user_id, limit)
    return jsonify([log.to_dict() for log in logs])

@therapeutic_bp.route('/dbt/skills/stats', methods=['GET'])
@demo_allowed
def get_skill_stats():
    """Get skill usage statistics"""
    user_id = get_current_user_id()
    days = request.args.get('days', 30, type=int)
    
    stats = TherapeuticRepository.get_skill_usage_stats(user_id, days)
    return jsonify(stats)

@therapeutic_bp.route('/dbt/skills/<skill_name>/effectiveness', methods=['GET'])
@demo_allowed
def get_skill_effectiveness(skill_name):
    """Get average effectiveness for a specific skill"""
    user_id = get_current_user_id()
    
    effectiveness = TherapeuticRepository.get_skill_effectiveness(user_id, skill_name)
    if effectiveness is not None:
        return jsonify({'skill_name': skill_name, 'average_effectiveness': effectiveness})
    return jsonify({'error': 'No data available'}), 404

# ===== DBT RECOMMENDATIONS =====

@therapeutic_bp.route('/dbt/recommendations', methods=['GET'])
@demo_allowed
def get_dbt_recommendations():
    """Get DBT skill recommendations"""
    user_id = get_current_user_id()
    situation_type = request.args.get('situation')
    
    recommendations = TherapeuticRepository.get_recommendations(user_id, situation_type)
    return jsonify([rec.to_dict() for rec in recommendations])

# ===== CRISIS RESOURCES =====

@therapeutic_bp.route('/crisis/resources', methods=['GET'])
@demo_allowed
def get_crisis_resources():
    """Get crisis resources"""
    user_id = get_current_user_id()
    emergency_only = request.args.get('emergency', 'false').lower() == 'true'
    
    resources = TherapeuticRepository.get_crisis_resources(user_id, emergency_only)
    return jsonify([resource.to_dict() for resource in resources])

@therapeutic_bp.route('/crisis/resources', methods=['POST'])
@demo_allowed
def add_crisis_resource():
    """Add a crisis resource"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or 'name' not in data or 'contact_info' not in data:
        return jsonify({'error': 'name and contact_info required'}), 400
    
    resource = TherapeuticRepository.add_crisis_resource(
        user_id=user_id,
        name=data['name'],
        contact_info=data['contact_info'],
        resource_type=data.get('resource_type', 'hotline'),
        is_emergency=data.get('is_emergency', False),
        notes=data.get('notes', '')
    )
    
    if resource:
        return jsonify(resource.to_dict()), 201
    return jsonify({'error': 'Failed to add resource'}), 500

# ===== DBT DIARY CARDS =====

@therapeutic_bp.route('/dbt/diary', methods=['POST'])
@demo_allowed
def create_diary_card():
    """Create a DBT diary card entry"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or 'date' not in data:
        return jsonify({'error': 'date required'}), 400
    
    try:
        date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    card = TherapeuticRepository.create_diary_card(
        user_id=user_id,
        date=date,
        emotions=data.get('emotions', {}),
        urges=data.get('urges', {}),
        skills_used=data.get('skills_used', []),
        notes=data.get('notes', '')
    )
    
    if card:
        return jsonify(card.to_dict()), 201
    return jsonify({'error': 'Failed to create diary card'}), 500

@therapeutic_bp.route('/dbt/diary', methods=['GET'])
@demo_allowed
def get_diary_cards():
    """Get diary cards for user"""
    user_id = get_current_user_id()
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    cards = TherapeuticRepository.get_diary_cards(user_id, start, end)
    return jsonify([card.to_dict() for card in cards])

# ===== AA ACHIEVEMENTS =====

@therapeutic_bp.route('/aa/achievements', methods=['GET'])
@demo_allowed
def get_achievements():
    """Get user's AA achievements"""
    user_id = get_current_user_id()
    
    achievements = TherapeuticRepository.get_user_achievements(user_id)
    total_points = TherapeuticRepository.get_total_points(user_id)
    
    return jsonify({
        'achievements': [ach.to_dict() for ach in achievements],
        'total_points': total_points
    })

@therapeutic_bp.route('/aa/achievements', methods=['POST'])
@demo_allowed
def award_achievement():
    """Award an achievement (admin/system use)"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'title required'}), 400
    
    achievement = TherapeuticRepository.award_achievement(
        user_id=user_id,
        achievement_type=data.get('type', 'milestone'),
        title=data['title'],
        description=data.get('description', ''),
        points=data.get('points', 10)
    )
    
    if achievement:
        return jsonify(achievement.to_dict()), 201
    return jsonify({'error': 'Failed to award achievement'}), 500

# ===== CBT THOUGHT RECORDS =====

@therapeutic_bp.route('/cbt/thoughts', methods=['POST'])
@demo_allowed
def create_thought_record():
    """Create a CBT thought record"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or 'situation' not in data:
        return jsonify({'error': 'situation required'}), 400
    
    # This would use a ThoughtRecord model when available
    return jsonify({
        'message': 'Thought record created',
        'id': 'demo_thought_1'
    }), 201

@therapeutic_bp.route('/cbt/thoughts', methods=['GET'])
@demo_allowed
def get_thought_records():
    """Get thought records for user"""
    user_id = get_current_user_id()
    
    # This would fetch actual thought records when model exists
    return jsonify([])

# ===== MOOD TRACKING =====

@therapeutic_bp.route('/mood', methods=['POST'])
@demo_allowed
def log_mood():
    """Log a mood entry"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or 'mood' not in data:
        return jsonify({'error': 'mood rating required'}), 400
    
    try:
        mood_rating = int(data['mood'])
        if not 1 <= mood_rating <= 10:
            return jsonify({'error': 'Mood rating must be between 1 and 10'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid mood rating'}), 400
    
    # This would use a MoodEntry model when available
    return jsonify({
        'id': 'demo_mood_1',
        'mood': mood_rating,
        'note': data.get('note', ''),
        'timestamp': datetime.utcnow().isoformat()
    }), 201

@therapeutic_bp.route('/mood', methods=['GET'])
@demo_allowed
def get_mood_entries():
    """Get mood entries for user"""
    user_id = get_current_user_id()
    
    # This would fetch actual mood entries when model exists
    return jsonify([])
