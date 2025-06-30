"""
Main application routes
"""

from flask import Blueprint, render_template, redirect, url_for, request, session
from utils.auth_compat import get_current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main landing page"""
    return redirect(url_for('public_demo'))

@main_bp.route('/chat')
def chat():
    """Main chat interface"""
    user = get_current_user()
    return render_template('chat.html', user=user)