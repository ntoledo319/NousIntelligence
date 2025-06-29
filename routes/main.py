"""
Main application routes
"""

from flask import Blueprint, render_template, redirect, url_for, request, session
from utils.auth_compat import login_required, get_demo_user, is_authenticated

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main landing page"""
    if is_authenticated():
        return redirect('/chat')
    return render_template('landing.html')

@main_bp.route('/chat')
def chat():
    """Main chat interface"""
    user = get_demo_user()
    return render_template('chat.html', user=user)

@main_bp.route('/demo')
def demo():
    """Public demo access"""
    # Allow public demo access
    demo_user = {
        'id': 'demo_user',
        'name': 'Demo User', 
        'email': 'demo@nous.app',
        'demo': True
    }
    return render_template('chat.html', user=demo_user, demo_mode=True)