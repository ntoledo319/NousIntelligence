"""
User routes and views.
Handles user-specific functionality like user guide and profile management.

@module user
@context_boundary User Interface
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
import logging
from models import db, User

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/guide')
def user_guide():
    """Display user guide page"""
    return render_template('user_guide.html')

@user_bp.route('/profile')
@login_required
def profile():
    """Display user profile page"""
    return render_template('profile.html', user=current_user)

@user_bp.route('/profile', methods=['POST'])
@login_required
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
        current_user.first_name = first_name
        current_user.last_name = last_name

        # Save to database
        db.session.commit()

        flash('Profile updated successfully', 'success')
        return redirect(url_for('user.profile'))
    except Exception as e:
        logging.error(f"Error updating profile: {str(e)}")
        flash(f'Error updating profile: {str(e)}', 'danger')
        return redirect(url_for('user.profile'))

@user_bp.route('/api/notifications')
@login_required
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