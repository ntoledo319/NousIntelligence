"""
Notification system routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, current_user, get_current_user

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/api/notifications')
def notifications_list():
    """Get notifications list"""
    return jsonify({
        'notifications': [
            {
                'id': 1,
                'message': 'Welcome to NOUS!',
                'type': 'info',
                'timestamp': '2025-06-29T06:00:00Z'
            }
        ]
    })
