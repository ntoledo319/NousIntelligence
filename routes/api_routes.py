"""
API Routes - Core API Endpoints
Provides RESTful API endpoints for the NOUS application
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint('api', __name__)

@api_bp.route('/chat', methods=['POST'])
def chat_api():
    """Chat API endpoint with fallback responses"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        demo_mode = data.get('demo_mode', True)  # Default to demo mode
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Simple fallback response system
        response_text = f"I understand your message: '{message}'. This is the demo version of NOUS. Full AI features will be available with proper API configuration."
        
        return jsonify({
            "response": response_text,
            "user": "Guest User",
            "timestamp": datetime.now().isoformat(),
            "demo": True,
            "fallback": "basic"
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({
            "response": "I'm experiencing some difficulty right now. Please try again shortly.",
            "error": True,
            "timestamp": datetime.now().isoformat()
        }), 500

@api_bp.route('/user')
def get_user():
    """Get current user info - supports guest mode"""
    return jsonify({
        'id': 'guest_user',
        'name': 'Guest User',
        'email': 'guest@nous.app',
        'avatar': '',
        'login_time': datetime.now().isoformat(),
        'is_guest': True,
        'demo_mode': True
    })

@api_bp.route('/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        "status": "operational",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "chat": "/api/v1/chat",
            "user": "/api/v1/user",
            "health": "/api/health"
        }
    })

# Export the blueprint
__all__ = ['api_bp']