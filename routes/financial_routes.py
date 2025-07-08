"""
Financial management routes
"""

from flask import Blueprint, render_template, jsonify, request
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

financial_bp = Blueprint('financial', __name__)

@financial_bp.route('/financial')
def financial_main():
    """Financial main page"""
    user = get_demo_user()
    return render_template('financial/main.html', user=user)

@financial_bp.route('/api/financial/accounts')
def financial_accounts():
    """Financial accounts API"""
    return jsonify({
        'accounts': [],
        'demo_mode': True
    })
