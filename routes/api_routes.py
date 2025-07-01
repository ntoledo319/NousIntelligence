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
    """Chat API endpoint with AI integration"""
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({
                "error": "Invalid JSON data",
                "message": "Please provide valid JSON with a 'message' field",
                "timestamp": datetime.now().isoformat()
            }), 400
            
        message = data.get('message', '').strip()
        demo_mode = data.get('demo_mode', True)  # Default to demo mode
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Try to use the unified AI service
        response_text = None
        provider = "fallback"
        ai_enabled = False
        
        try:
            from utils.unified_ai_service import get_unified_ai_service
            ai_service = get_unified_ai_service()
            
            # Generate AI response
            ai_response_text = ai_service.get_ai_response(message)
            
            if ai_response_text and ai_response_text.strip():
                ai_response = {
                    'success': True,
                    'content': ai_response_text,
                    'provider': 'ai'
                }
            else:
                ai_response = {'success': False}
            
            if ai_response and ai_response.get('success'):
                response_text = ai_response.get('content', ai_response.get('response', 'No response generated'))
                provider = ai_response.get('provider', 'ai')
                ai_enabled = True
                logger.info(f"AI response generated successfully using {provider}")
            else:
                response_text = f"I understand your message: '{message}'. I'm having trouble connecting to AI services right now, but I'm here to help!"
                
        except ImportError as e:
            logger.warning(f"AI service import failed: {e}")
            response_text = f"I understand your message: '{message}'. AI services are being initialized - please try again in a moment."
        except Exception as e:
            logger.error(f"AI service error: {e}")
            response_text = f"I understand your message: '{message}'. I'm having some trouble with AI processing right now, but I'm still here to assist you."
        
        # Fallback if no response generated
        if not response_text:
            response_text = f"I understand your message: '{message}'. This is the demo version of NOUS with AI capabilities!"
        
        return jsonify({
            "response": response_text,
            "user": "Guest User",
            "timestamp": datetime.now().isoformat(),
            "demo": demo_mode,
            "provider": provider,
            "ai_enabled": ai_enabled,
            "fallback": not ai_enabled
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