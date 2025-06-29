"""
Chat routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, current_user, get_current_user

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
def chat_page():
    """Chat interface"""
    user = get_current_user()
    return render_template('chat.html', user=user)

@chat_bp.route('/api/chat', methods=['POST'])
def chat_api():
    """Chat API endpoint"""
    data = request.get_json() or {}
    message = data.get('message', '')
    user = get_current_user()
    
    response = {
        'response': f"Hello {user['name']}! You said: {message}",
        'user': user,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    return jsonify(response)
