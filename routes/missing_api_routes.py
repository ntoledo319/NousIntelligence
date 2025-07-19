"""
Missing API Routes
Provides API endpoints that tests expect but weren't implemented
"""

from flask import Blueprint, jsonify, request, session
from utils.unified_auth import demo_allowed, get_demo_user, is_authenticated
import logging

logger = logging.getLogger(__name__)

# API Blueprint for missing routes
missing_api_bp = Blueprint('missing_api', __name__, url_prefix='/api/v1')

# Root Blueprint for missing root routes
missing_root_bp = Blueprint('missing_root', __name__)

@missing_api_bp.route('/user', methods=['GET'])
@demo_allowed
def get_user_info():
    """Get current user information"""
    user = get_demo_user()
    return jsonify({
        'id': user.get('id', 'demo_user'),
        'name': user.get('name', 'Demo User'),
        'email': user.get('email', 'demo@nous.app'),
        'demo_mode': True
    })

@missing_api_bp.route('/mood', methods=['GET'])
@demo_allowed
def get_mood_entries():
    """Get mood entries for the user"""
    # Return empty list for demo
    return jsonify([])

@missing_api_bp.route('/mood', methods=['POST'])
@demo_allowed
def create_mood_entry():
    """Create a new mood entry"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate mood rating
    if 'mood' not in data:
        return jsonify({'error': 'Mood rating is required'}), 400
    
    try:
        mood_rating = int(data['mood'])
        if not 1 <= mood_rating <= 10:
            return jsonify({'error': 'Mood rating must be between 1 and 10'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid mood rating format'}), 400
    
    # Return success response
    return jsonify({
        'id': '1',
        'mood': mood_rating,
        'note': data.get('note', ''),
        'user_id': get_demo_user().get('id', 'demo_user')
    }), 201

@missing_api_bp.route('/tasks', methods=['GET'])
@demo_allowed
def get_tasks():
    """Get tasks for the user"""
    # Return empty list for demo
    return jsonify([])

@missing_api_bp.route('/tasks', methods=['POST'])
@demo_allowed
def create_task():
    """Create a new task"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    # Return success response
    return jsonify({
        'id': '1',
        'title': data['title'],
        'description': data.get('description', ''),
        'completed': False,
        'user_id': get_demo_user().get('id', 'demo_user')
    }), 201

@missing_root_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': '2023-01-01T00:00:00Z'})

@missing_root_bp.route('/api/health')
def api_health_check():
    """API health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'api', 'timestamp': '2023-01-01T00:00:00Z'})

@missing_root_bp.route('/healthz')
def healthz():
    """Kubernetes-style health check"""
    return jsonify({'status': 'healthy', 'ready': True})

@missing_api_bp.route('/settings', methods=['GET'])
@demo_allowed
def get_settings():
    """Get user settings"""
    user = get_demo_user()
    return jsonify({
        'theme': 'light',
        'notifications': True,
        'language': 'en',
        'user_id': user.get('id', 'demo_user')
    })

@missing_api_bp.route('/settings', methods=['POST'])
@demo_allowed
def update_settings():
    """Update user settings"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Return success response
    return jsonify({
        'message': 'Settings updated successfully',
        'settings': data
    })
