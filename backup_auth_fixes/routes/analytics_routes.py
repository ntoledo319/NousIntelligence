"""
Analytics and insights routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, current_user, get_current_user

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def analytics_main():
    """Analytics main page"""
    user = get_current_user()
    return render_template('analytics/main.html', user=user)

@analytics_bp.route('/api/analytics/summary')
def analytics_summary():
    """Analytics summary API"""
    return jsonify({
        'summary': {
            'total_sessions': 1,
            'total_messages': 0,
            'avg_session_length': '5 minutes'
        }
    })
