"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required', 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for('login'))

def get_current_user():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

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