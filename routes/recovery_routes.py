"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required', 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for('login'))

def get_current_user():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

Routes for Recovery Insights and Progress Tracking
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for

from utils.aa_helper import get_recovery_stats
from utils.ai_helper import generate_ai_text

recovery_bp = Blueprint('recovery_routes', __name__, url_prefix='/recovery')

@recovery_bp.route('/insights')
def insights_dashboard():
    """Renders the main recovery insights dashboard."""
    user_id = session.get('user', {}).get('id', 'demo_user')
    
    # Get recovery stats
    stats = get_recovery_stats(user_id)
    
    # This is a placeholder for more advanced AI insights.
    # A real implementation would fetch journal entries and other data
    # to generate more personalized insights.
    insight_prompt = f"Based on the following recovery stats, provide a brief, encouraging insight for the user: {stats}"
    ai_insight = generate_ai_text(insight_prompt)

    return render_template('recovery_insights.html', stats=stats, insight=ai_insight) 