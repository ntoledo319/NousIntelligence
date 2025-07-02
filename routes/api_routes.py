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

def _generate_demo_response(message):
    """Generate intelligent demo responses based on message patterns"""
    message_lower = message.lower().strip()
    
    # Greeting patterns
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon']):
        return "Hello! I'm NOUS, your AI assistant. I'm currently running in demo mode, which means I can chat with you and answer questions using my basic capabilities. How can I help you today?"
    
    # Question patterns
    if message_lower.startswith('what'):
        return f"That's an interesting question! You asked: '{message}'. In demo mode, I can provide helpful responses and engage in conversations. My full AI capabilities would give you even more detailed and accurate answers."
    
    if message_lower.startswith('how'):
        return f"Great question about '{message}'! I can help explain concepts and provide guidance. In full mode, I'd have access to more comprehensive knowledge and reasoning capabilities."
    
    if message_lower.startswith('why'):
        return f"You're asking about '{message}' - that's thoughtful! I enjoy exploring the 'why' behind things. In demo mode, I can share insights and engage in meaningful discussions about topics like this."
    
    # Help patterns
    if any(word in message_lower for word in ['help', 'assist', 'support', 'can you']):
        return "I'm here to help! Even in demo mode, I can assist with conversations, answer questions, provide explanations, and engage in meaningful discussions. What specific topic would you like to explore?"
    
    # Thank you patterns
    if any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return "You're very welcome! I'm glad I could help. Feel free to ask me anything else - I enjoy our conversations!"
    
    # Default conversational response
    return f"I understand you said: '{message}'. That's interesting! I'm NOUS, your AI assistant in demo mode. I'm designed to be helpful, informative, and engaging. What would you like to talk about or explore together?"

def generate_fallback_response(message):
    """Generate simple pattern-based responses when AI services are unavailable"""
    message_lower = message.lower().strip()
    
    # Greeting patterns
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! I'm NOUS, your AI assistant. How can I help you today?"
    
    # Question patterns
    if message_lower.startswith('what'):
        return f"That's an interesting question about '{message}'. I'm currently running in demo mode with limited AI capabilities, but I'd be happy to help you explore this topic further!"
    
    if message_lower.startswith('how'):
        return f"Great question! While I'm in demo mode, I can tell you that '{message}' is something I'd normally help you with using my full AI capabilities."
    
    if message_lower.startswith('why'):
        return f"I understand you're asking about '{message}'. In full mode, I can provide detailed explanations and insights about topics like this."
    
    # Help patterns
    if any(word in message_lower for word in ['help', 'assist', 'support']):
        return "I'm here to help! I'm currently in demo mode, but I can assist with conversations, answer questions, and provide guidance on various topics."
    
    # Default response
    return f"I understand you said: '{message}'. I'm NOUS, your AI assistant running in demo mode. While my full AI capabilities are initializing, I'm still here to chat and help however I can!"

@api_bp.route('/chat', methods=['POST'])
def chat_api():
    """Chat API endpoint with robust fallback system"""
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
        
        # Generate response using simple pattern-based system
        response_text = _generate_demo_response(message)
        provider = "demo_assistant"
        ai_enabled = False
        
        # Try to enhance with AI if available
        try:
            from utils.unified_ai_service import get_unified_ai_service
            ai_service = get_unified_ai_service()
            ai_response = ai_service.get_ai_response(message)
            
            if ai_response and ai_response.strip():
                response_text = ai_response
                provider = "ai_enhanced"
                ai_enabled = True
                logger.info("Enhanced response with AI service")
                
        except Exception as e:
            logger.info(f"AI enhancement unavailable: {e}, using demo response")
        
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
            "response": "Hello! I'm NOUS, your AI assistant. I'm here to help with any questions or conversations you'd like to have.",
            "error": False,
            "timestamp": datetime.now().isoformat(),
            "provider": "emergency_fallback"
        })

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