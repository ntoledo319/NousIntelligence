"""
Core Chat Module - CHAT-FIRST UNIFICATION
Auto-discovery and registration system for chat handlers
"""

try:
    from .blueprint import chat_bp
    from .dispatcher import ChatDispatcher
    from .handler_registry import HandlerRegistry
    
    __all__ = ['chat_bp', 'ChatDispatcher', 'HandlerRegistry']
except ImportError as e:
    print(f"Warning: Chat module import error: {e}")
    chat_bp = None
    ChatDispatcher = None
    HandlerRegistry = None
    __all__ = []