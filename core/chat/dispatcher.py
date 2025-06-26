"""
Chat Dispatcher - Routes messages to appropriate handlers
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Callable
from .handler_registry import HandlerRegistry

class ChatDispatcher:
    """Main chat message dispatcher with auto-routing"""
    
    def __init__(self):
        self.registry = HandlerRegistry()
        self.middleware: List[Callable] = []
        self.fallback_handler = None
    
    def add_middleware(self, middleware_func: Callable) -> None:
        """Add middleware to the dispatcher"""
        self.middleware.append(middleware_func)
    
    def set_fallback_handler(self, handler: Callable) -> None:
        """Set fallback handler for unmatched messages"""
        self.fallback_handler = handler
    
    async def dispatch(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Dispatch a message to the appropriate handler"""
        if context is None:
            context = {}
        
        # Apply middleware
        for middleware in self.middleware:
            try:
                message, context = await self._apply_middleware(middleware, message, context)
            except Exception as e:
                print(f"Middleware error: {e}")
        
        # Find appropriate handler
        handler_info = self.registry.find_handler(message)
        
        if handler_info:
            return await self._execute_handler(handler_info, message, context)
        elif self.fallback_handler:
            return await self._execute_fallback(message, context)
        else:
            return await self._default_response(message, context)
    
    async def _apply_middleware(self, middleware: Callable, message: str, context: Dict[str, Any]) -> tuple:
        """Apply middleware function"""
        if asyncio.iscoroutinefunction(middleware):
            return await middleware(message, context)
        else:
            return middleware(message, context)
    
    async def _execute_handler(self, handler_info: Dict[str, Any], message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the matched handler"""
        try:
            # Try to load handler if not already loaded
            if handler_info['callable'] is None:
                handler_info['callable'] = await self._load_handler(handler_info)
            
            handler_func = handler_info['callable']
            
            if handler_func:
                if asyncio.iscoroutinefunction(handler_func):
                    result = await handler_func(message, context)
                else:
                    result = handler_func(message, context)
                
                return {
                    'success': True,
                    'response': result,
                    'handler': handler_info['function'],
                    'type': handler_info['type']
                }
            else:
                return await self._handler_not_found(handler_info, message, context)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'handler': handler_info['function'],
                'message': 'Handler execution failed'
            }
    
    async def _load_handler(self, handler_info: Dict[str, Any]) -> Optional[Callable]:
        """Dynamically load a handler function"""
        try:
            file_path = handler_info['file']
            function_name = handler_info['function']
            
            # Convert file path to module path
            if file_path.endswith('.py'):
                module_path = file_path[:-3].replace('/', '.')
                
                # Import the module and get the function
                import importlib
                module = importlib.import_module(module_path)
                
                if hasattr(module, function_name):
                    return getattr(module, function_name)
                    
        except Exception as e:
            print(f"Error loading handler {handler_info['function']}: {e}")
        
        return None
    
    async def _execute_fallback(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fallback handler"""
        try:
            if asyncio.iscoroutinefunction(self.fallback_handler):
                result = await self.fallback_handler(message, context)
            else:
                result = self.fallback_handler(message, context)
            
            return {
                'success': True,
                'response': result,
                'handler': 'fallback',
                'type': 'fallback'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'handler': 'fallback',
                'message': 'Fallback handler failed'
            }
    
    async def _handler_not_found(self, handler_info: Dict[str, Any], message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case where handler function couldn't be loaded"""
        return {
            'success': False,
            'error': 'Handler function not found',
            'handler': handler_info['function'],
            'message': f"Could not load handler from {handler_info['file']}",
            'suggestion': f"TODO: Implement {handler_info['function']} in {handler_info['file']}"
        }
    
    async def _default_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Default response when no handler is found"""
        return {
            'success': False,
            'response': "I'm not sure how to help with that. Could you try rephrasing your request?",
            'handler': 'default',
            'type': 'default',
            'available_handlers': [h['function'] for h in self.registry.list_handlers()]
        }
    
    def generate_handler_stubs(self) -> List[Dict[str, str]]:
        """Generate TODO stubs for missing handlers"""
        stubs = []
        
        for handler_info in self.registry.list_handlers():
            if handler_info['callable'] is None:
                stub_code = self._generate_stub_code(handler_info)
                stubs.append({
                    'file': handler_info['file'],
                    'function': handler_info['function'],
                    'code': stub_code
                })
        
        return stubs
    
    def _generate_stub_code(self, handler_info: Dict[str, Any]) -> str:
        """Generate stub code for a handler"""
        function_name = handler_info['function']
        patterns = ', '.join(f'"{p}"' for p in handler_info['intent_patterns'][:3])
        
        return f'''
async def {function_name}(message: str, context: dict) -> str:
    """
    TODO: Implement {function_name}
    
    Handles messages matching patterns: {patterns}
    
    Args:
        message: The user's message
        context: Request context
        
    Returns:
        Response string
    """
    return f"TODO: {function_name} not yet implemented. Message was: {{message}}"
'''
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dispatcher statistics"""
        handlers = self.registry.list_handlers()
        
        return {
            'total_handlers': len(handlers),
            'loaded_handlers': len([h for h in handlers if h['callable'] is not None]),
            'middleware_count': len(self.middleware),
            'has_fallback': self.fallback_handler is not None,
            'handlers_by_type': {
                handler_type: len([h for h in handlers if h['type'] == handler_type])
                for handler_type in set(h['type'] for h in handlers)
            }
        }