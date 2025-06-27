"""
Messaging Status and Capability Handler
Documents what messaging features are and are not available
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Define what messaging capabilities are available
MESSAGING_CAPABILITIES = {
    "sms": False,
    "text_message": False,
    "phone_notification": False,
    "email": True,  # Email is available via existing services
    "app_notification": True,  # In-app notifications are available
    "push_notification": False,  # Push notifications not implemented
    "twilio": False,  # Twilio SMS not implemented
}

# Clear error messages for unavailable features
SMS_NOT_AVAILABLE_MESSAGE = "SMS and text messaging features are not currently available in this system. Please use email notifications or in-app alerts instead."

def check_messaging_capability(capability: str) -> bool:
    """
    Check if a messaging capability is available
    
    Args:
        capability: The messaging capability to check (e.g., 'sms', 'email', 'app_notification')
    
    Returns:
        bool: True if capability is available, False otherwise
    """
    return MESSAGING_CAPABILITIES.get(capability.lower(), False)

def get_available_messaging_methods() -> Dict[str, bool]:
    """
    Get all available messaging methods
    
    Returns:
        Dict of messaging methods and their availability status
    """
    return MESSAGING_CAPABILITIES.copy()

def get_sms_error_response() -> Dict[str, Any]:
    """
    Get standard error response for SMS requests
    
    Returns:
        Dict containing error information
    """
    return {
        "success": False,
        "error": "SMS_NOT_AVAILABLE",
        "message": SMS_NOT_AVAILABLE_MESSAGE,
        "alternatives": [
            "Use email notifications instead",
            "Set up in-app notifications",
            "Use the web dashboard for alerts"
        ],
        "available_methods": [method for method, available in MESSAGING_CAPABILITIES.items() if available]
    }

def handle_text_message_request(phone_number: Optional[str] = None, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Handle any text message request with clear error message
    
    Args:
        phone_number: Phone number (ignored)
        message: Message to send (ignored)
    
    Returns:
        Dict containing error response
    """
    logger.warning("Text message request attempted but SMS is not available")
    return get_sms_error_response()

def handle_sms_request(**kwargs) -> Dict[str, Any]:
    """
    Handle any SMS request with clear error message
    
    Args:
        **kwargs: Any SMS-related parameters (ignored)
    
    Returns:
        Dict containing error response
    """
    logger.warning("SMS request attempted but SMS is not available")
    return get_sms_error_response()

def validate_notification_method(method: str) -> bool:
    """
    Validate if a notification method is available
    
    Args:
        method: Notification method to validate
    
    Returns:
        bool: True if method is available, False otherwise
    """
    if method.lower() in ['sms', 'text', 'text_message', 'phone']:
        return False
    if method.lower() in ['email', 'app', 'app_notification', 'web']:
        return True
    return False

def get_alternative_notification_methods() -> list:
    """
    Get list of alternative notification methods when SMS is requested
    
    Returns:
        List of available notification methods
    """
    return [
        "email",
        "app_notification", 
        "web_dashboard",
        "browser_notification"
    ]

def log_sms_attempt(context: str = "Unknown"):
    """
    Log attempts to use SMS functionality for monitoring
    
    Args:
        context: Context of where SMS was attempted
    """
    logger.info(f"SMS functionality attempted in context: {context}. SMS is not available.")

# Export the main functions and constants
__all__ = [
    'MESSAGING_CAPABILITIES',
    'SMS_NOT_AVAILABLE_MESSAGE',
    'check_messaging_capability',
    'get_available_messaging_methods',
    'get_sms_error_response',
    'handle_text_message_request',
    'handle_sms_request',
    'validate_notification_method',
    'get_alternative_notification_methods',
    'log_sms_attempt'
]