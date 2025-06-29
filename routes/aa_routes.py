"""
from utils.auth_compat import get_demo_user
AA (Alcoholics Anonymous) support routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, get_demo_user(), get_get_demo_user()

aa_bp = Blueprint('aa', __name__)

@aa_bp.route('/aa')
def aa_main():
    """AA main page"""
    user = get_get_demo_user()()
    return render_template('aa/main.html', user=user)

@aa_bp.route('/api/aa/steps')
def aa_steps():
    """AA steps API"""
    return jsonify({
        'steps': [f"Step {i}" for i in range(1, 13)]
    })
