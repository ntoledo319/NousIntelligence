"""
CBT (Cognitive Behavioral Therapy) routes
"""

from flask import Blueprint, render_template, jsonify, request, session
from datetime import datetime, timedelta
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
from models.database import db
from models.health_models import CBTThoughtRecord, CBTMoodLog
import logging

logger = logging.getLogger(__name__)
cbt_bp = Blueprint('cbt', __name__)

def get_current_user_id():
    """Get current user ID from session"""
    return session.get('user_id', 'demo_user')

@cbt_bp.route('/cbt')
def cbt_main():
    """CBT main page"""
    user = get_demo_user()
    return render_template('cbt/dashboard.html', user=user)

@cbt_bp.route('/cbt/dashboard')
@demo_allowed
def dashboard():
    """CBT dashboard"""
    user = get_demo_user()
    return render_template('cbt/dashboard.html', user=user)

@cbt_bp.route('/cbt/thought-records')
@demo_allowed
def thought_records():
    """View all thought records"""
    user_id = get_current_user_id()
    try:
        records = CBTThoughtRecord.query.filter_by(user_id=user_id).order_by(CBTThoughtRecord.created_at.desc()).all()
        thoughts = [r.to_dict() for r in records]
    except Exception as e:
        logger.error(f"Error fetching thought records: {e}")
        thoughts = []
    
    return render_template('cbt/thought_records.html', thoughts=thoughts)

@cbt_bp.route('/cbt/thought-records/new')
@demo_allowed
def new_thought_record():
    """Create new thought record form"""
    return render_template('cbt/new_thought_record.html')

@cbt_bp.route('/cbt/thought-records/<int:record_id>')
@demo_allowed
def view_thought_record(record_id):
    """View specific thought record"""
    user_id = get_current_user_id()
    try:
        record = CBTThoughtRecord.query.filter_by(id=record_id, user_id=user_id).first()
        if record:
            return render_template('cbt/view_thought_record.html', thought=record.to_dict())
    except Exception as e:
        logger.error(f"Error fetching thought record: {e}")
    
    return render_template('cbt/error.html', error="Thought record not found"), 404

@cbt_bp.route('/cbt/mood-tracking')
@demo_allowed
def mood_tracking():
    """Mood tracking page"""
    user_id = get_current_user_id()
    try:
        mood_trends = get_mood_trends(user_id, days=30)
    except Exception as e:
        logger.error(f"Error fetching mood trends: {e}")
        mood_trends = {'success': False, 'data': []}
    
    return render_template('cbt/mood_tracking.html', mood_trends=mood_trends)

# API Routes

@cbt_bp.route('/api/cbt/exercises')
def cbt_exercises():
    """CBT exercises API"""
    return jsonify({
        'exercises': [
            'Thought Records',
            'Behavioral Experiments',
            'Mood Tracking',
            'Cognitive Restructuring'
        ]
    })

@cbt_bp.route('/cbt/api/thought-records', methods=['POST'])
@demo_allowed
def create_thought_record_api():
    """Create new thought record"""
    user_id = get_current_user_id()
    data = request.get_json() or {}
    
    try:
        record = CBTThoughtRecord(
            user_id=user_id,
            situation=data.get('situation', ''),
            automatic_thought=data.get('automatic_thought', ''),
            emotion=data.get('emotion'),
            emotion_intensity=data.get('emotion_intensity'),
            physical_symptoms=data.get('physical_symptoms')
        )
        
        db.session.add(record)
        db.session.commit()
        
        identified_biases = identify_cognitive_biases(data.get('automatic_thought', ''))
        
        return jsonify({
            'success': True,
            'data': record.to_dict(),
            'identified_biases': identified_biases
        })
    except Exception as e:
        logger.error(f"Error creating thought record: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@cbt_bp.route('/cbt/api/thought-records/<int:record_id>', methods=['PUT'])
@demo_allowed
def update_thought_record_api(record_id):
    """Update thought record with challenge data"""
    user_id = get_current_user_id()
    data = request.get_json() or {}
    
    try:
        record = CBTThoughtRecord.query.filter_by(id=record_id, user_id=user_id).first()
        if not record:
            return jsonify({'success': False, 'error': 'Record not found'}), 404
        
        record.evidence_for = data.get('evidence_for', record.evidence_for)
        record.evidence_against = data.get('evidence_against', record.evidence_against)
        record.balanced_thought = data.get('balanced_thought', record.balanced_thought)
        record.new_emotion = data.get('new_emotion', record.new_emotion)
        record.new_emotion_intensity = data.get('new_emotion_intensity', record.new_emotion_intensity)
        record.behavioral_response = data.get('behavioral_response', record.behavioral_response)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': record.to_dict()
        })
    except Exception as e:
        logger.error(f"Error updating thought record: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@cbt_bp.route('/cbt/api/mood', methods=['POST'])
@demo_allowed
def log_mood_api():
    """Log mood entry"""
    user_id = get_current_user_id()
    data = request.get_json() or {}
    
    try:
        mood_log = CBTMoodLog(
            user_id=user_id,
            mood=data.get('primary_emotion'),
            intensity=data.get('emotion_intensity'),
            triggers=data.get('triggers'),
            notes=data.get('thoughts'),
            physical_symptoms=data.get('physical_symptoms'),
            coping_strategy_used=data.get('coping_strategy_used'),
            effectiveness_rating=data.get('effectiveness_rating')
        )
        
        db.session.add(mood_log)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': mood_log.to_dict()
        })
    except Exception as e:
        logger.error(f"Error logging mood: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@cbt_bp.route('/cbt/api/mood/trends')
@demo_allowed
def get_mood_trends_api():
    """Get mood trends and analysis"""
    user_id = get_current_user_id()
    days = request.args.get('days', 30, type=int)
    
    try:
        trends = get_mood_trends(user_id, days)
        return jsonify(trends)
    except Exception as e:
        logger.error(f"Error getting mood trends: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@cbt_bp.route('/cbt/api/cognitive-biases', methods=['POST'])
@demo_allowed
def identify_biases_api():
    """Identify cognitive biases in thought"""
    data = request.get_json() or {}
    thought = data.get('thought', '')
    
    try:
        biases = identify_cognitive_biases(thought)
        return jsonify({
            'success': True,
            'identified_biases': biases
        })
    except Exception as e:
        logger.error(f"Error identifying biases: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@cbt_bp.route('/cbt/api/ai-assistant', methods=['POST'])
@demo_allowed
def cbt_ai_assistant():
    """AI assistant for CBT exercises"""
    data = request.get_json() or {}
    user_input = data.get('user_input', '')
    context = data.get('context', 'general')
    
    try:
        from services.emotion_aware_therapeutic_assistant import EmotionAwareTherapeuticAssistant
        assistant = EmotionAwareTherapeuticAssistant()
        user_id = get_current_user_id()
        
        response = assistant.get_therapeutic_response(
            user_input=user_input,
            user_id=user_id,
            context={'cbt_context': context}
        )
        
        return jsonify({
            'success': True,
            'response': response.get('response', {}).get('text', 'I\'m here to help guide you through this CBT exercise.')
        })
    except Exception as e:
        logger.error(f"Error with CBT AI assistant: {e}")
        return jsonify({
            'success': False,
            'error': 'AI assistance temporarily unavailable'
        }), 500

# Helper Functions

def get_mood_trends(user_id, days=30):
    """Calculate mood trends for user"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        moods = CBTMoodLog.query.filter(
            CBTMoodLog.user_id == user_id,
            CBTMoodLog.timestamp >= cutoff_date
        ).order_by(CBTMoodLog.timestamp.desc()).all()
        
        if not moods:
            return {
                'success': True,
                'total_entries': 0,
                'average_intensity': 0,
                'most_common_emotion': None,
                'patterns': [],
                'data': [],
                'period': f'Last {days} days'
            }
        
        total_intensity = sum(m.intensity or 0 for m in moods if m.intensity)
        avg_intensity = round(total_intensity / len(moods), 1) if moods else 0
        
        emotion_counts = {}
        for m in moods:
            if m.mood:
                emotion_counts[m.mood] = emotion_counts.get(m.mood, 0) + 1
        
        most_common = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
        
        patterns = []
        if avg_intensity >= 7:
            patterns.append("High emotional intensity - consider coping strategies")
        if most_common:
            patterns.append(f"Most frequent emotion: {most_common.title()}")
        
        return {
            'success': True,
            'total_entries': len(moods),
            'average_intensity': avg_intensity,
            'most_common_emotion': most_common.title() if most_common else None,
            'patterns': patterns,
            'data': [m.to_dict() for m in moods],
            'period': f'Last {days} days'
        }
    except Exception as e:
        logger.error(f"Error calculating mood trends: {e}")
        return {'success': False, 'error': str(e)}

def identify_cognitive_biases(thought):
    """Identify cognitive biases in automatic thought"""
    biases = []
    thought_lower = thought.lower()
    
    bias_patterns = {
        'All-or-Nothing Thinking': {
            'keywords': ['always', 'never', 'every time', 'completely', 'totally'],
            'description': 'Seeing things in black-and-white categories',
            'reframe': 'Look for middle ground and exceptions'
        },
        'Catastrophizing': {
            'keywords': ['disaster', 'terrible', 'worst', 'ruin', 'end'],
            'description': 'Expecting the worst possible outcome',
            'reframe': 'What\'s the most likely outcome? What can you control?'
        },
        'Overgeneralization': {
            'keywords': ['everyone', 'nobody', 'everything', 'nothing'],
            'description': 'Drawing broad conclusions from single events',
            'reframe': 'Is this really true in all cases? What are the exceptions?'
        },
        'Mind Reading': {
            'keywords': ['they think', 'must think', 'probably thinks', 'knows i'],
            'description': 'Assuming you know what others are thinking',
            'reframe': 'Do you have evidence for this? Could you ask them directly?'
        },
        'Should Statements': {
            'keywords': ['should', 'must', 'ought to', 'have to'],
            'description': 'Using rigid rules about how things "should" be',
            'reframe': 'Replace "should" with "it would be nice if" or "I prefer"'
        },
        'Labeling': {
            'keywords': ['i am a', 'i\'m such a', 'i\'m so'],
            'description': 'Attaching a negative label to yourself',
            'reframe': 'Describe the behavior, not your whole identity'
        }
    }
    
    for bias_name, bias_info in bias_patterns.items():
        if any(keyword in thought_lower for keyword in bias_info['keywords']):
            biases.append({
                'name': bias_name,
                'description': bias_info['description'],
                'reframe_suggestion': bias_info['reframe']
            })
    
    return biases
