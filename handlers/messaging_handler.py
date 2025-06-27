"""
Messaging Handler - Handles requests for text messaging and provides clear status
"""

import logging
from typing import Dict, Any
from utils.messaging_status import (
    get_sms_error_response, 
    get_available_messaging_methods,
    get_alternative_notification_methods,
    log_sms_attempt
)

logger = logging.getLogger(__name__)

async def handle_text_message_intent(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle requests for text messaging functionality
    
    Args:
        message: User's message
        context: Request context
    
    Returns:
        Response explaining SMS is not available
    """
    log_sms_attempt("Chat message handler")
    
    # Check if user is asking about SMS capabilities
    sms_keywords = ['text', 'sms', 'message', 'phone', 'send text', 'text message']
    message_lower = message.lower()
    
    if any(keyword in message_lower for keyword in sms_keywords):
        available_methods = get_available_messaging_methods()
        alternatives = get_alternative_notification_methods()
        
        response_text = (
            "I understand you're asking about text messaging. "
            "SMS and text messaging features are not currently available in this system. "
            "\n\nHere's what I can help you with instead:\n"
            "• Email notifications\n"
            "• In-app notifications and alerts\n"
            "• Web dashboard notifications\n"
            "\nWould you like me to help you set up any of these alternative notification methods?"
        )
        
        return {
            'success': True,
            'response': response_text,
            'handler': 'messaging_handler',
            'type': 'capability_info',
            'data': {
                'requested_feature': 'sms',
                'available': False,
                'alternatives': alternatives,
                'available_methods': {k: v for k, v in available_methods.items() if v}
            }
        }
    
    # If not specifically about messaging, return None to let other handlers process
    return None

async def handle_notification_setup(message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle requests to set up notifications
    
    Args:
        message: User's message
        context: Request context
    
    Returns:
        Response about notification setup options
    """
    notification_keywords = ['notification', 'alert', 'notify', 'remind', 'email alert']
    message_lower = message.lower()
    
    if any(keyword in message_lower for keyword in notification_keywords):
        if 'sms' in message_lower or 'text' in message_lower:
            # User wants SMS notifications - redirect to alternatives
            return await handle_text_message_intent(message, context)
        
        response_text = (
            "I can help you set up notifications! Here are the available options:\n\n"
            "• **Email Notifications** - Get alerts via email\n"
            "• **In-App Notifications** - See alerts in the web dashboard\n"
            "• **Price Alerts** - Get notified when product prices change\n"
            "• **Calendar Reminders** - Appointment and event notifications\n"
            "\nWhich type of notification would you like to set up?"
        )
        
        return {
            'success': True,
            'response': response_text,
            'handler': 'messaging_handler',
            'type': 'notification_setup',
            'data': {
                'available_notifications': [
                    'email',
                    'in_app',
                    'price_alerts',
                    'calendar_reminders'
                ]
            }
        }
    
    return None

# Register intent patterns for auto-discovery
INTENT_PATTERNS = [
    "send text",
    "text message",
    "sms",
    "phone message",
    "send sms",
    "text notification",
    "mobile notification",
    "phone notification",
    "messaging",
    "can you text",
    "send me a text",
    "notification setup",
    "set up alerts",
    "alert me",
    "notify me"
]

# Handler functions for registration
HANDLERS = {
    'text_message_intent': handle_text_message_intent,
    'notification_setup': handle_notification_setup
}

__all__ = ['handle_text_message_intent', 'handle_notification_setup', 'INTENT_PATTERNS', 'HANDLERS']