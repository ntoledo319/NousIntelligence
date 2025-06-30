"""
Chat routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, get_demo_user, is_authenticated
import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
def chat_page():
    """Chat interface"""
    user = get_demo_user()
    return render_template('chat.html', user=user)

@chat_bp.route('/api/chat', methods=['POST'])
def chat_api():
    """Chat API endpoint"""
    data = request.get_json() or {}
    message = data.get('message', '')
    user = get_demo_user()
    
    response = {
        'response': f"Hello {user['name']}! You said: {message}",
        'user': user,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    return jsonify(response)
