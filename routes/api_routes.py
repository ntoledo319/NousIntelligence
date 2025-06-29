"""
from utils.auth_compat import get_demo_user
API routes for NOUS application
"""

from flask import Blueprint, jsonify, request, session
from utils.auth_compat import get_get_demo_user(), require_authentication

api_bp = Blueprint('api', __name__)

@api_bp.route('/chat', methods=['POST'])
def chat_api():
    """Chat API endpoint with demo support"""
    data = request.get_json() or {}
    message = data.get('message', '')
    
    # Get user (demo or authenticated)
    user = get_get_demo_user()()
    
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
    user = get_get_demo_user()()
    return jsonify(user)