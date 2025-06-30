"""
Main Routes - Landing Page and Core Application Routes
Handles the main application landing page and core routing
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify

logger = logging.getLogger(__name__)

# Create main blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Landing page for NOUS application"""
    try:
        # Check if user is authenticated
        user_authenticated = 'user' in session and session['user'] is not None
        
        # Get OAuth availability from app config
        from flask import current_app
        oauth_available = current_app.config.get('OAUTH_ENABLED', True)  # Default to True for better UX
        
        return render_template('landing.html', 
                             user_authenticated=user_authenticated,
                             oauth_available=oauth_available)
    except Exception as e:
        logger.error(f"Landing page error: {e}")
        return render_template('landing.html', 
                             user_authenticated=False,
                             oauth_available=False)

@main_bp.route('/dashboard')
def dashboard():
    """Main dashboard - redirects to chat for demo"""
    # Set demo user in session
    session['user'] = {
        'id': 'demo_user_123',
        'name': 'Demo User',
        'email': 'demo@nous.app',
        'demo_mode': True
    }
    return redirect('/chat')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/features')
def features():
    """Features page"""
    return render_template('features.html')

@main_bp.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html')

@main_bp.route('/demo')
def demo():
    """Demo page for NOUS"""
    try:
        # Create demo user session
        session['user'] = {
            'id': 'demo_user_123',
            'name': 'Demo User',
            'email': 'demo@nous.app',
            'demo_mode': True
        }
        
        # Redirect to chat with demo mode
        return redirect('/chat')
    except Exception as e:
        logger.error(f"Demo page error: {e}")
        return "Demo mode temporarily unavailable", 500

# Export the blueprint
__all__ = ['main_bp']