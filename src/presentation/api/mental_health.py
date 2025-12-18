from flask import Blueprint, jsonify, request
from src.infrastructure.di_container import container
from utils.unified_auth import demo_allowed, get_demo_user
from utils.encryption import encrypt_field, decrypt_field
import logging

logger = logging.getLogger(__name__)

mental_health_bp = Blueprint('mental_health', __name__, url_prefix='/api/mental_health')

@mental_health_bp.route('/health')
def health():
    """Health check for mental_health service"""
    return jsonify({'status': 'healthy', 'service': 'mental_health'})

@mental_health_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@mental_health_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error in mental_health: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@mental_health_bp.route('/mood', methods=['POST'])
def log_mood():
    """Log a mood entry"""
    data = request.get_json()
    
    # Validate required fields
    if not data or 'mood' not in data:
        return jsonify({'error': 'Mood rating is required'}), 400
    
    # Validate mood rating (1-10)
    try:
        mood_rating = int(data['mood'])
        if not 1 <= mood_rating <= 10:
            return jsonify({'error': 'Mood rating must be between 1 and 10'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid mood rating format'}), 400
    
    # In a real implementation, this would save the mood entry
    # For now, return a success response
    return jsonify({
        'id': '1',
        'mood': mood_rating,
        'note': data.get('note', ''),
        'user_id': get_demo_user().get('id', 'demo_user')
    }), 201

@mental_health_bp.route('/thought-record', methods=['POST'])
@demo_allowed
def create_thought_record():
    """Create a thought record"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['situation', 'thoughts', 'emotions', 'intensity']
    if not all(field in data for field in required_fields):
        missing = [field for field in required_fields if field not in data]
        return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
    
    # Validate intensity (1-10)
    try:
        intensity = int(data['intensity'])
        if not 1 <= intensity <= 10:
            return jsonify({'error': 'Intensity must be between 1 and 10'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid intensity format'}), 400
    
    # In a real implementation, this would save the thought record
    # For now, return a success response
    return jsonify({
        'id': '1',
        'situation': data['situation'],
        'thoughts': data['thoughts'],
        'emotions': data['emotions'],
        'intensity': intensity,
        'user_id': get_demo_user().get('id', 'demo_user'),
        'created_at': '2023-01-01T00:00:00Z'
    }), 201
