"""
Feedback API Module
Handles user feedback collection for beta testing program
"""

from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

# Create feedback API blueprint
feedback_api = Blueprint('feedback_api', __name__, url_prefix='/api/feedback')

@feedback_api.route('/submit', methods=['POST'])
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Basic validation
        required_fields = ['feedback', 'rating']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Log feedback (in production, this would be stored in database)
        logger.info(f"Feedback received: {data}")
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@feedback_api.route('/status', methods=['GET'])
def feedback_status():
    """Get feedback system status"""
    return jsonify({
        'status': 'operational',
        'system': 'feedback_api',
        'version': '1.0.0'
    })