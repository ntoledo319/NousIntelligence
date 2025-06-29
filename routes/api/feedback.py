"""
from utils.auth_compat import get_demo_user
Feedback API routes
"""

from flask import Blueprint, request, jsonify
from utils.auth_compat import login_required, get_demo_user(), get_get_demo_user()

feedback_api = Blueprint('feedback_api', __name__)

@feedback_api.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback"""
    data = request.get_json() or {}
    user = get_get_demo_user()()
    
    feedback_data = {
        'user_id': user.get('id') if user else 'anonymous',
        'rating': data.get('rating'),
        'message': data.get('message', ''),
        'category': data.get('category', 'general'),
        'timestamp': 'now'
    }
    
    return jsonify({
        'status': 'success',
        'message': 'Feedback submitted successfully',
        'data': feedback_data
    })

@feedback_api.route('/api/feedback', methods=['GET'])
def get_feedback():
    """Get feedback list"""
    return jsonify({
        'feedback': [
            {
                'id': 1,
                'rating': 5,
                'message': 'Great app!',
                'category': 'general',
                'timestamp': '2025-06-29T07:00:00Z'
            }
        ]
    })