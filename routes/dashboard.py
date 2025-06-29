"""
from utils.auth_compat import get_demo_user
Dashboard routes
"""

from flask import Blueprint, render_template, jsonify
from utils.auth_compat import login_required, get_demo_user(), get_get_demo_user()

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Main dashboard"""
    user = get_get_demo_user()()
    return render_template('dashboard.html', user=user)

@dashboard_bp.route('/api/dashboard/stats')
def dashboard_stats():
    """Dashboard statistics API"""
    user = get_get_demo_user()()
    return jsonify({
        'user': user,
        'stats': {
            'messages': 0,
            'sessions': 1
        }
    })
