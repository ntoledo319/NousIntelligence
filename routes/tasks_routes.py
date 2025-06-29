"""
Task management routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, current_user, get_current_user

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/tasks')
def tasks_main():
    """Tasks main page"""
    user = get_current_user()
    return render_template('tasks/main.html', user=user)

@tasks_bp.route('/api/tasks')
def tasks_list():
    """Tasks list API"""
    return jsonify({
        'tasks': [
            {'id': 1, 'title': 'Demo Task', 'completed': False}
        ]
    })
