"""
Chat Routes - Chat Interface and Related Endpoints
Provides web interface for the chat functionality
"""

import logging
from datetime import datetime
from flask import Blueprint, render_template, session

logger = logging.getLogger(__name__)

# Create chat blueprint
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
def chat_interface():
    """Main chat interface page"""
    try:
        # Ensure demo user is in session
        if 'user' not in session:
            session['user'] = {
                'id': 'demo_user_123',
                'name': 'Demo User',
                'email': 'demo@nous.app',
                'demo_mode': True
            }
        
        return render_template('chat.html', user=session['user'])
    except Exception as e:
        logger.error(f"Chat interface error: {e}")
        # Fallback to basic chat interface
        demo_user = {
            'id': 'demo_user_123',
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'demo_mode': True
        }
        return render_template('chat.html', user=demo_user)

@chat_bp.route('/chat/demo')
def demo_chat():
    """Demo chat interface"""
    demo_user = {
        'id': 'demo_user_123',
        'name': 'Demo User',
        'email': 'demo@nous.app',
        'demo_mode': True,
        'login_time': datetime.now().isoformat()
    }
    return render_template('chat.html', user=demo_user, demo_mode=True)

# Export the blueprint
__all__ = ['chat_bp']