"""
API Routes - Core API Endpoints (CSRF Protected Version)
Provides RESTful API endpoints for the NOUS application with CSRF protection
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from functools import wraps

logger = logging.getLogger(__name__)

# Import CSRF protection
try:
    from utils.csrf_protection import csrf_protect, generate_csrf_token
except ImportError:
    # Fallback CSRF protection
    def csrf_protect(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
                session_token = session.get('csrf_token')
                
                if not token or not session_token or token != session_token:
                    return jsonify({'error': 'CSRF token validation failed'}), 403
            return f(*args, **kwargs)
        return decorated_function
    
    def generate_csrf_token():
        import secrets
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return session['csrf_token']

# Create API blueprint
api_bp = Blueprint('api', __name__)

def validate_json_input(required_fields=None):
    """Decorator to validate JSON input with proper error handling"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                data = request.get_json(force=False)
                if data is None:
                    return jsonify({
                        'error': 'Invalid JSON data',
                        'message': 'Request must contain valid JSON'
                    }), 400
                
                # Check required fields
                if required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        return jsonify({
                            'error': 'Missing required fields',
                            'missing_fields': missing_fields
                        }), 400
                
                # Add validated data to kwargs
                kwargs['validated_data'] = data
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"JSON validation error: {e}")
                return jsonify({
                    'error': 'JSON parsing failed',
                    'message': 'Invalid JSON format'
                }), 400
        return decorated_function
    return decorator

@api_bp.route('/chat', methods=['POST'])
@csrf_protect
@validate_json_input(['message'])
def chat_api(validated_data):
    """Chat API endpoint with AI integration and CSRF protection"""
    try:
        message = validated_data.get('message', '').strip()
        demo_mode = validated_data.get('demo_mode', True)
        
        if not message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # Validate message length
        if len(message) > 1000:
            return jsonify({'error': 'Message too long (max 1000 characters)'}), 400
        
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
            "fallback": not ai_enabled,
            "csrf_token": generate_csrf_token()  # Include fresh CSRF token
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({
            "response": "I'm experiencing some difficulty right now. Please try again shortly.",
            "error": True,
            "timestamp": datetime.now().isoformat(),
            "csrf_token": generate_csrf_token()
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
        'demo_mode': True,
        'csrf_token': generate_csrf_token()
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
        },
        "security": {
            "csrf_protection": True,
            "input_validation": True
        }
    })

# Export the blueprint
__all__ = ['api_bp']