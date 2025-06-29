"""
Financial management routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.auth_compat import login_required, current_user, get_current_user

financial_bp = Blueprint('financial', __name__)

@financial_bp.route('/financial')
@login_required
def financial_main():
    """Financial main page"""
    user = get_current_user()
    return render_template('financial/main.html', user=user)

@financial_bp.route('/api/financial/accounts')
@login_required
def financial_accounts():
    """Financial accounts API"""
    return jsonify({
        'accounts': [],
        'demo_mode': True
    })
