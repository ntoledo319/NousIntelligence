"""
Chat Blueprint - Flask Blueprint for chat routes with SocketIO support
"""

from flask import Blueprint, request, jsonify, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from typing import Dict, Any
import asyncio
import json

from .dispatcher import ChatDispatcher
from services.nlu_service import nlu_service
from services.therapeutic_content_service import therapeutic_content_service

# Create blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/core/chat')

# Initialize dispatcher
dispatcher = ChatDispatcher()

# SocketIO instance (will be set by app)
socketio = None

def init_socketio(socketio_instance):
    """Initialize SocketIO instance"""
    global socketio
    socketio = socketio_instance

@chat_bp.route('/health')
def chat_health():
    """Health check for chat system"""
    stats = dispatcher.get_stats()
    return jsonify({
        'status': 'healthy',
        'dispatcher_stats': stats
    })

@chat_bp.route('/handlers')
def list_handlers():
    """List all registered chat handlers"""
    handlers = dispatcher.registry.list_handlers()
    return jsonify({
        'handlers': handlers,
        'count': len(handlers)
    })

@chat_bp.route('/message', methods=['POST'])
def handle_message():
    """Handle chat message via REST API"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        context = data.get('context', {})
        
        # Add request context
        context.update({
            'method': 'REST',
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        })
        
        # Dispatch message
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(dispatcher.dispatch(message, context))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to process message'
        }), 500

@chat_bp.route('/stubs')
def generate_stubs():
    """Generate handler stubs for missing functions"""
    try:
        stubs = dispatcher.generate_handler_stubs()
        return jsonify({
            'stubs': stubs,
            'count': len(stubs)
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to generate stubs'
        }), 500

@chat_bp.route('/debug')
def debug_info():
    """Debug information for chat system"""
    try:
        # Load codegraph for debugging
        with open('/tmp/codegraph.json', 'r') as f:
            codegraph = json.load(f)
        
        return jsonify({
            'dispatcher_stats': dispatcher.get_stats(),
            'handlers': dispatcher.registry.list_handlers(),
            'codegraph_summary': codegraph.get('summary', {}),
            'middleware_count': len(dispatcher.middleware),
            'has_fallback': dispatcher.fallback_handler is not None
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Debug info unavailable'
        }), 500

# SocketIO Event Handlers
def register_socketio_handlers():
    """Register SocketIO event handlers"""
    
    @socketio.on('connect', namespace='/chat')
    def on_connect():
        """Handle client connection"""
        emit('status', {'message': 'Connected to chat system'})
    
    @socketio.on('disconnect', namespace='/chat')
    def on_disconnect():
        """Handle client disconnection"""
        print('Client disconnected from chat')
    
    @socketio.on('join_room', namespace='/chat')
    def on_join_room(data):
        """Handle room joining"""
        room = data.get('room', 'default')
        join_room(room)
        emit('status', {'message': f'Joined room: {room}'})
    
    @socketio.on('leave_room', namespace='/chat')
    def on_leave_room(data):
        """Handle room leaving"""
        room = data.get('room', 'default')
        leave_room(room)
        emit('status', {'message': f'Left room: {room}'})
    
    @socketio.on('message', namespace='/chat')
    def on_message(data):
        """Handle incoming chat message via SocketIO"""
        try:
            message = data.get('message', '')
            context = data.get('context', {})
            room = data.get('room', 'default')
            
            # Add SocketIO context
            context.update({
                'method': 'SocketIO',
                'room': room,
                'session_id': request.sid
            })
            
            # Dispatch message asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(dispatcher.dispatch(message, context))
            loop.close()
            
            # Emit result
            emit('response', result, room=room)
            
        except Exception as e:
            emit('error', {
                'error': str(e),
                'message': 'Failed to process message'
            })

# Chat Interface Route
@chat_bp.route('/')
def chat_interface():
    """Render chat interface"""
    return render_template('chat/interface.html', 
                         handlers=dispatcher.registry.list_handlers(),
                         stats=dispatcher.get_stats())

# Auto-setup middleware and fallback
def setup_default_handlers():
    """Setup default middleware and fallback handlers"""
    
    # Default message preprocessing middleware
    def preprocess_message(message: str, context: Dict[str, Any]) -> tuple:
        """Preprocess incoming messages"""
        # Clean up message
        message = message.strip()
        
        # Add timestamp
        import time
        context['timestamp'] = time.time()
        
        return message, context

    # NLU + safety tagging middleware
    def apply_nlu(message: str, context: Dict[str, Any]) -> tuple:
        """Tag message with intents, language, and crisis signals"""
        nlu_result = nlu_service.analyze(message, context.get('user_id'), context=context)
        context['nlu'] = nlu_result.to_dict()
        context['locale'] = context.get('locale') or nlu_result.language
        context['dialogue_mode'] = context.get('dialogue_mode') or ('crisis' if nlu_result.crisis else 'wellness')
        return message, context
    
    # Default fallback handler
    def default_fallback(message: str, context: Dict[str, Any]) -> str:
        """Default fallback when no handler matches"""
        return f"I understand you said: '{message}', but I don't have a specific handler for that yet. Try asking about available commands or features."

    def retrieval_first_fallback(message: str, context: Dict[str, Any]) -> Any:
        """Fallback that prefers vetted therapeutic content before a generic reply"""
        nlu_payload = context.get('nlu', {})
        locale = context.get('locale') or nlu_payload.get('language') or 'en'
        tags = nlu_payload.get('tags', [])
        content = therapeutic_content_service.get_best_content(
            tags=tags,
            locale=locale,
            intent=nlu_payload.get('primary_intent'),
            emotion=nlu_payload.get('emotion')
        )

        if content:
            return {
                'text': content.get('summary') or default_fallback(message, context),
                'title': content.get('title'),
                'steps': content.get('steps', []),
                'quick_replies': content.get('quick_replies', []),
                'locale': locale,
                'safety': content.get('safety', {}),
                'type': 'retrieval_fallback'
            }

        return default_fallback(message, context)
    
    # Register defaults
    dispatcher.add_middleware(preprocess_message)
    dispatcher.add_middleware(apply_nlu)
    dispatcher.set_fallback_handler(retrieval_first_fallback)

# Initialize defaults when blueprint is imported
setup_default_handlers()

# Export functions for app integration
__all__ = ['chat_bp', 'dispatcher', 'init_socketio', 'register_socketio_handlers']
