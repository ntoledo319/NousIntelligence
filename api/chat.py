"""
Unified /api/chat dispatcher
Auto-registers handlers and routes messages by intent pattern
"""

import json
import asyncio
from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import sys
import os

# Add core to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from core.chat.dispatcher import ChatDispatcher
    from core.chat.handler_registry import HandlerRegistry
except ImportError:
    # Fallback if core chat system not available
    class ChatDispatcher:
        def __init__(self):
            self.handlers = {}
            self.registry = None
        
        async def dispatch(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
            return {
                'success': True,
                'response': f"Echo: {message}",
                'handler': 'fallback',
                'type': 'echo'
            }
        
        def get_stats(self) -> Dict[str, Any]:
            return {
                'total_handlers': 0,
                'loaded_handlers': 0,
                'middleware_count': 0,
                'has_fallback': True
            }
    
    class HandlerRegistry:
        def __init__(self):
            self.handlers = {}

# Create API blueprint
api_chat_bp = Blueprint('api_chat', __name__, url_prefix='/api')

# Initialize dispatcher
dispatcher = ChatDispatcher()

@api_chat_bp.route('/chat', methods=['POST'])
def api_chat():
    """Main chat API endpoint with auto-routing"""
    try:
        # Get request data
        data = request.get_json() or {}
        message = data.get('message', '').strip()
        context = data.get('context', {})
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'No message provided',
                'message': 'Please provide a message in the request body'
            }), 400
        
        # Add request context
        context.update({
            'method': 'API',
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'content_type': request.headers.get('Content-Type', ''),
            'endpoint': '/api/chat'
        })
        
        # Dispatch message
        try:
            # Create event loop for async dispatch
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(dispatcher.dispatch(message, context))
            loop.close()
            
            return jsonify(result)
            
        except Exception as dispatch_error:
            return jsonify({
                'success': False,
                'error': str(dispatch_error),
                'message': 'Failed to dispatch message',
                'fallback_response': f"I received your message: '{message}' but encountered an error processing it."
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'API request processing failed'
        }), 500

@api_chat_bp.route('/chat/handlers', methods=['GET'])
def list_chat_handlers():
    """List all available chat handlers"""
    try:
        if hasattr(dispatcher, 'registry'):
            handlers = dispatcher.registry.list_handlers()
            stats = dispatcher.get_stats()
        else:
            handlers = []
            stats = {'total_handlers': 0}
        
        return jsonify({
            'handlers': handlers,
            'stats': stats,
            'endpoint': '/api/chat'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to list handlers'
        }), 500

@api_chat_bp.route('/chat/health', methods=['GET'])
def chat_api_health():
    """Health check for chat API"""
    try:
        # Test basic functionality
        test_message = "health check"
        test_context = {'test': True}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(dispatcher.dispatch(test_message, test_context))
        loop.close()
        
        return jsonify({
            'status': 'healthy',
            'api_version': '1.0',
            'dispatcher_available': True,
            'test_result': result.get('success', False),
            'handlers_loaded': getattr(dispatcher, 'registry', {}).get('total_handlers', 0) if hasattr(dispatcher, 'registry') else 0
        })
        
    except Exception as e:
        return jsonify({
            'status': 'degraded',
            'error': str(e),
            'dispatcher_available': False
        }), 503

# Manual handler registration function
def register_chat_handler(intent_patterns: list, handler_func):
    """Manually register a chat handler function"""
    try:
        if hasattr(dispatcher, 'registry'):
            dispatcher.registry.register_handler(intent_patterns, handler_func)
            return True
    except Exception as e:
        print(f"Failed to register handler: {e}")
    return False

# Auto-discovery function
def auto_discover_handlers():
    """Auto-discover and register handlers from codegraph"""
    try:
        # Load codegraph
        with open('/tmp/codegraph.json', 'r') as f:
            codegraph = json.load(f)
        
        discovered_count = 0
        
        # Process chat handlers from codegraph
        for handler_info in codegraph.get('chat_handlers', []):
            function_name = handler_info.get('function', '')
            file_path = handler_info.get('file', '')
            
            if function_name and file_path:
                try:
                    # Try to import and register the handler
                    module_path = file_path.replace('.py', '').replace('/', '.')
                    if module_path.startswith('.'):
                        module_path = module_path[1:]
                    
                    # Import module and get function
                    import importlib
                    module = importlib.import_module(module_path)
                    
                    if hasattr(module, function_name):
                        handler_func = getattr(module, function_name)
                        
                        # Generate intent patterns
                        patterns = _generate_intent_patterns(function_name)
                        
                        # Register handler
                        if register_chat_handler(patterns, handler_func):
                            discovered_count += 1
                            print(f"Auto-registered handler: {function_name}")
                        
                except Exception as e:
                    print(f"Failed to auto-register {function_name}: {e}")
        
        print(f"Auto-discovery complete: {discovered_count} handlers registered")
        return discovered_count
        
    except Exception as e:
        print(f"Auto-discovery failed: {e}")
        return 0

def _generate_intent_patterns(function_name: str) -> list:
    """Generate intent patterns from function name"""
    patterns = []
    
    if function_name.startswith('cmd_'):
        command = function_name[4:]
        patterns.extend([f"/{command}", command])
    elif function_name.startswith('handle_'):
        action = function_name[7:]
        patterns.append(action)
    elif 'chat' in function_name.lower():
        patterns.append('chat')
    
    # Add variations
    base_patterns = patterns.copy()
    for pattern in base_patterns:
        patterns.extend([
            pattern.replace('_', ' '),
            pattern.replace('-', ' '),
            pattern.lower()
        ])
    
    return list(set(patterns))

# Initialize auto-discovery on import
try:
    auto_discover_handlers()
except Exception as e:
    print(f"Initial auto-discovery failed: {e}")

# Export blueprint
__all__ = ['api_chat_bp', 'register_chat_handler', 'auto_discover_handlers']