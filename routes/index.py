"""
Index Routes - Main application landing page and public routes
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

index_bp = Blueprint('index', __name__)

@index_bp.route('/demo')  
def demo():
    """Demo chat interface with modern UI"""
    user = get_demo_user()
    return render_template('app.html', user=user, demo_mode=True)

@index_bp.route('/public')
def public():
    """Public access page"""
    user = get_demo_user()
    return render_template('app.html', user=user, demo_mode=True)