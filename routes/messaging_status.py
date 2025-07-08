"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Messaging Status Routes
Messaging Status functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

messaging_status_bp = Blueprint('messaging_status', __name__)


def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_get_demo_user()():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

Messaging Status Routes
Handles real-time messaging status and notifications
"""

from flask import Blueprint, request, jsonify, session
import logging
from datetime import datetime

messaging_bp = Blueprint('messaging', __name__)

@messaging_bp.route('/status', methods=['GET'])
def get_messaging_status():
    """Get current messaging system status"""
    try:
        return jsonify({
            'success': True,
            'status': 'online',
            'message_queue_size': 0,
            'last_updated': datetime.utcnow().isoformat(),
            'connections': {
                'active': 0,
                'total': 0
            }
        })
    except Exception as e:
        logging.error(f"Messaging status error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get messaging status'
        }), 500

@messaging_bp.route('/send', methods=['POST'])
def send_message():
    """Send a message through the messaging system"""
    try:
        data = request.get_json() or {}
        message = data.get('message', '')
        recipient = data.get('recipient', '')
        
        if not message or not recipient:
            return jsonify({
                'success': False,
                'error': 'Message and recipient required'
            }), 400
        
        # In a real implementation, send through messaging system
        return jsonify({
            'success': True,
            'message_id': f"msg_{datetime.utcnow().timestamp()}",
            'status': 'sent',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logging.error(f"Message send error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to send message'
        }), 500

@messaging_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Get user notifications"""
    try:
        return jsonify({
            'success': True,
            'notifications': [],
            'unread_count': 0,
            'last_check': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logging.error(f"Notifications error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get notifications'
        }), 500