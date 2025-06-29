"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, current_user, get_current_user, is_authenticated
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

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

Deployment Health Check Routes
Essential for deployment success monitoring
"""
from flask import Blueprint, jsonify
import datetime
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
@health_bp.route('/healthz')
def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Basic health indicators
        health_data = {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": os.environ.get('FLASK_ENV', 'production'),
            "port": os.environ.get('PORT', '5000')
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        error_data = {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }
        return jsonify(error_data), 500

@health_bp.route('/ready')
def readiness_check():
    """Readiness check for deployment"""
    return jsonify({"status": "ready"}), 200
