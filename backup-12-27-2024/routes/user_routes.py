"""
User Routes

This module provides routes for user account management,
including profile viewing and editing.
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

# Create blueprint
user_bp = Blueprint('user', __name__, url_prefix='/user')

# Set up logger
logger = logging.getLogger(__name__)

@user_bp.route('/profile')
@login_required
def profile():
    """Display user profile page"""
    return render_template('user/profile.html')

@user_bp.route('/preferences')
@login_required
def preferences():
    """Display user preferences page"""
    return render_template('user/preferences.html')

@user_bp.route('/activity')
@login_required
def activity():
    """Display user activity history"""
    return render_template('user/activity.html')