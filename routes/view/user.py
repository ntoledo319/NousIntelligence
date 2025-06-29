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

User routes and views.
Handles user-specific functionality like user guide and profile management.

@module user
@context_boundary User Interface
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify

import logging
from models import db, User

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/guide')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def user_guide():
    """Display user guide page"""
    return render_template('user_guide.html')

@user_bp.route('/profile')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def profile():
    """Display user profile page"""
    return render_template('profile.html', user=session.get('user'))

@user_bp.route('/profile', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def update_profile():
    """Update user profile information"""
    try:
        # Get form data
        first_name = request.form.get('first_name', '')
        last_name = request.form.get('last_name', '')

        # Validate data
        if not first_name or not last_name:
            flash('First name and last name are required', 'danger')
            return redirect(url_for('user.profile'))

        # Update user data
        session.get('user', {}).get('first_name = first_name
        session.get('user', {}).get('last_name = last_name

        # Save to database
        db.session.commit()

        flash('Profile updated successfully', 'success')
        return redirect(url_for('user.profile'))
    except Exception as e:
        logging.error(f"Error updating profile: {str(e)}")
        flash(f'Error updating profile: {str(e)}', 'danger')
        return redirect(url_for('user.profile'))

@user_bp.route('/api/notifications')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def get_notifications():
    """API endpoint to get user notifications"""
    # This is a placeholder for actual notification functionality
    # In a real implementation, you would fetch notifications from a database
    try:
        notifications = []

        # Example notifications
        notifications = [
            {
                'id': 1,
                'type': 'appointment',
                'message': 'Doctor appointment tomorrow at 10:00 AM',
                'date': '2023-07-15T10:00:00',
                'read': False
            },
            {
                'id': 2,
                'type': 'medication',
                'message': 'Medication refill needed: Lisinopril (5 days left)',
                'date': '2023-07-14T09:00:00',
                'read': True
            },
            {
                'id': 3,
                'type': 'system',
                'message': 'NOUS was updated to version 1.0.5',
                'date': '2023-07-13T15:30:00',
                'read': False
            }
        ]

        return jsonify({
            'success': True,
            'notifications': notifications,
            'unread_count': sum(1 for n in notifications if not n['read'])
        })
    except Exception as e:
        logging.error(f"Error fetching notifications: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e),
            'notifications': [],
            'unread_count': 0
        })