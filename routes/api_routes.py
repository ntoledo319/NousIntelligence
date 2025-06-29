"""
API routes for NOUS application
"""

from flask import Blueprint, jsonify, request, session
from utils.auth_compat import login_required, get_demo_user, is_authenticated

api_bp = Blueprint('api', __name__)

@api_bp.route('/chat', methods=['POST'])
def chat_api():
    """Chat API endpoint with demo support"""
    data = request.get_json() or {}
    message = data.get('message', '')
    
    # Get user (demo or authenticated)
    user = get_demo_user()()
    
    # Simple response for now
    response = {
        'response': f"Hello {user['name']}! You said: {message}",
        'user': user,
        'demo_mode': user.get('demo', False)
    }
    
    return jsonify(response)

@api_bp.route('/user')
def api_user():
    """Get current user info"""
    user = get_demo_user()()
    return jsonify(user)