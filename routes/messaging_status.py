"""
Messaging Status API Endpoints
Provides clear information about available and unavailable messaging features
"""

from flask import Blueprint, jsonify, request
from utils.messaging_status import (
    get_available_messaging_methods,
    get_sms_error_response,
    get_alternative_notification_methods,
    check_messaging_capability,
    log_sms_attempt
)

# Create blueprint
messaging_bp = Blueprint('messaging_status', __name__, url_prefix='/api/messaging')

@messaging_bp.route('/capabilities', methods=['GET'])
def get_messaging_capabilities():
    """
    Get all messaging capabilities and their availability status
    
    Returns:
        JSON response with messaging capabilities
    """
    try:
        capabilities = get_available_messaging_methods()
        alternatives = get_alternative_notification_methods()
        
        return jsonify({
            'success': True,
            'capabilities': capabilities,
            'available_methods': [method for method, available in capabilities.items() if available],
            'unavailable_methods': [method for method, available in capabilities.items() if not available],
            'alternatives': alternatives
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve messaging capabilities'
        }), 500

@messaging_bp.route('/sms/status', methods=['GET'])
def get_sms_status():
    """
    Get SMS status - always returns unavailable with alternatives
    
    Returns:
        JSON response indicating SMS is not available
    """
    log_sms_attempt("SMS status check via API")
    return jsonify(get_sms_error_response())

@messaging_bp.route('/sms/send', methods=['POST'])
def send_sms():
    """
    Handle SMS send requests - always returns error with alternatives
    
    Returns:
        JSON response indicating SMS is not available
    """
    log_sms_attempt("SMS send attempt via API")
    
    # Log the attempted request for monitoring
    data = request.get_json() or {}
    phone_number = data.get('phone_number', 'unknown')
    message = data.get('message', 'unknown')
    
    # Return clear error message
    response = get_sms_error_response()
    response['attempted_request'] = {
        'phone_number': phone_number[:3] + '***' if phone_number != 'unknown' else 'unknown',
        'message_length': len(message) if message != 'unknown' else 0
    }
    
    return jsonify(response), 400

@messaging_bp.route('/check/<capability>', methods=['GET'])
def check_capability(capability):
    """
    Check if a specific messaging capability is available
    
    Args:
        capability: The capability to check (e.g., 'sms', 'email', 'app_notification')
    
    Returns:
        JSON response with capability status
    """
    try:
        is_available = check_messaging_capability(capability)
        
        if not is_available and capability.lower() in ['sms', 'text', 'text_message']:
            log_sms_attempt(f"Capability check for {capability}")
            return jsonify({
                'success': True,
                'capability': capability,
                'available': False,
                'message': f'{capability} is not currently supported',
                'alternatives': get_alternative_notification_methods()
            })
        
        return jsonify({
            'success': True,
            'capability': capability,
            'available': is_available,
            'message': f'{capability} is {"available" if is_available else "not available"}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to check capability: {capability}'
        }), 500

@messaging_bp.route('/alternatives', methods=['GET'])
def get_alternatives():
    """
    Get alternative notification methods
    
    Returns:
        JSON response with alternative notification methods
    """
    try:
        alternatives = get_alternative_notification_methods()
        available = get_available_messaging_methods()
        
        return jsonify({
            'success': True,
            'alternatives': alternatives,
            'available_methods': {k: v for k, v in available.items() if v},
            'recommendations': [
                {
                    'method': 'email',
                    'description': 'Send email notifications for important alerts',
                    'setup_required': True
                },
                {
                    'method': 'app_notification',
                    'description': 'Display notifications in the web dashboard',
                    'setup_required': False
                },
                {
                    'method': 'web_dashboard',
                    'description': 'View alerts and notifications in the web interface',
                    'setup_required': False
                }
            ]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve alternatives'
        }), 500

# Export blueprint
__all__ = ['messaging_bp']