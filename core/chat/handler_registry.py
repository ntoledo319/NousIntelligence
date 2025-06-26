"""
Handler Registry - Auto-discovery system for chat handlers
"""

import json
import inspect
from typing import Dict, List, Callable, Any, Optional
from pathlib import Path

class HandlerRegistry:
    """Registry for chat handlers with auto-discovery"""
    
    def __init__(self):
        self.handlers: Dict[str, Dict[str, Any]] = {}
        self.load_codegraph()
    
    def load_codegraph(self) -> None:
        """Load the code graph to find handlers"""
        try:
            with open('/tmp/codegraph.json', 'r') as f:
                codegraph = json.load(f)
            
            # Register handlers from codegraph
            for handler in codegraph.get('chat_handlers', []):
                self.register_handler_from_codegraph(handler)
                
        except Exception as e:
            print(f"Warning: Could not load codegraph: {e}")
    
    def register_handler_from_codegraph(self, handler_info: Dict[str, Any]) -> None:
        """Register a handler from codegraph data"""
        function_name = handler_info['function']
        file_path = handler_info.get('file', '')
        
        # Extract intent patterns from function name
        intent_patterns = self._extract_intent_patterns(function_name)
        
        self.handlers[function_name] = {
            'function': function_name,
            'file': file_path,
            'intent_patterns': intent_patterns,
            'type': handler_info.get('type', 'unknown'),
            'callable': None  # Will be set when loaded
        }
    
    def _extract_intent_patterns(self, function_name: str) -> List[str]:
        """Extract intent patterns from function name"""
        patterns = []
        
        # Extract patterns based on naming conventions
        if function_name.startswith('cmd_'):
            command = function_name[4:]  # Remove 'cmd_'
            patterns.append(f"/{command}")
            patterns.append(command)
        
        elif function_name.startswith('handle_'):
            action = function_name[7:]  # Remove 'handle_'
            patterns.append(action)
        
        elif 'chat' in function_name.lower():
            # Generic chat handler
            patterns.append('chat')
        
        # Add common variations
        base_patterns = patterns.copy()
        for pattern in base_patterns:
            patterns.extend([
                pattern.replace('_', ' '),
                pattern.replace('-', ' '),
                pattern.lower(),
                pattern.upper()
            ])
        
        return list(set(patterns))  # Remove duplicates
    
    def register_handler(self, intent_patterns: List[str], handler_func: Callable) -> None:
        """Manually register a handler function"""
        function_name = handler_func.__name__
        
        self.handlers[function_name] = {
            'function': function_name,
            'file': inspect.getfile(handler_func),
            'intent_patterns': intent_patterns,
            'type': 'manual',
            'callable': handler_func
        }
    
    def find_handler(self, message: str) -> Optional[Dict[str, Any]]:
        """Find the best handler for a message"""
        message_lower = message.lower().strip()
        
        best_match = None
        best_score = 0
        
        for handler_name, handler_info in self.handlers.items():
            score = self._calculate_match_score(message_lower, handler_info['intent_patterns'])
            
            if score > best_score:
                best_score = score
                best_match = handler_info
        
        return best_match if best_score > 0 else None
    
    def _calculate_match_score(self, message: str, patterns: List[str]) -> int:
        """Calculate how well a message matches intent patterns"""
        score = 0
        
        for pattern in patterns:
            pattern_lower = pattern.lower()
            
            # Exact match
            if message == pattern_lower:
                score += 100
            
            # Starts with pattern
            elif message.startswith(pattern_lower):
                score += 50
            
            # Contains pattern
            elif pattern_lower in message:
                score += 25
            
            # Word boundary match
            elif f" {pattern_lower} " in f" {message} ":
                score += 75
        
        return score
    
    def list_handlers(self) -> List[Dict[str, Any]]:
        """List all registered handlers"""
        return list(self.handlers.values())
    
    def get_handler_info(self, handler_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific handler"""
        return self.handlers.get(handler_name)