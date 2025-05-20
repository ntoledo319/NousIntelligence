"""
Chat Command Router
==================

This module routes chat commands to appropriate handlers based on the user's intent.
It serves as the central hub for processing chat messages and determining the right
specialized handler for each command.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple

# Import command handlers for different features
from routes.chat_meet_commands import handle_meet_command, COMMAND_PATTERNS as MEET_PATTERNS

logger = logging.getLogger(__name__)

# Dictionary mapping feature domains to their command pattern dictionaries
DOMAIN_PATTERNS = {
    'meet': MEET_PATTERNS,
    # Add other domains as they're implemented:
    # 'spotify': SPOTIFY_PATTERNS,
    # 'tasks': TASK_PATTERNS,
    # 'calendar': CALENDAR_PATTERNS,
    # etc.
}

def process_chat_command(user_id: int, message: str) -> Dict[str, Any]:
    """
    Process a chat message and route it to the appropriate command handler
    
    Args:
        user_id: The ID of the current user
        message: The chat message text from the user
        
    Returns:
        Response dictionary containing the command results
    """
    # First, determine which domain (feature area) this command belongs to
    domain, command_type = identify_command_domain(message)
    
    if not domain:
        # No specific command identified, treat as general conversation
        return {
            'success': True,
            'message': "I didn't recognize that as a specific command. You can ask me to create meetings, generate agendas, or analyze notes.",
            'is_command': False
        }
    
    # Route to the appropriate domain handler
    if domain == 'meet':
        return handle_meet_command(user_id, message)
    # Add other domain handlers as they're implemented
    # elif domain == 'spotify':
    #     return handle_spotify_command(user_id, message)
    # etc.
    
    # Fallback if domain identified but no handler available
    return {
        'success': False,
        'message': f"I understood you wanted to do something with {domain}, but I don't have a handler for that yet.",
        'is_command': True
    }

def identify_command_domain(message: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Identify which domain and command type a message belongs to
    
    Args:
        message: The chat message text
        
    Returns:
        Tuple of (domain, command_type) or (None, None) if not identified
    """
    for domain, patterns in DOMAIN_PATTERNS.items():
        for cmd_type, cmd_patterns in patterns.items():
            for pattern in cmd_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return domain, cmd_type
    
    return None, None 