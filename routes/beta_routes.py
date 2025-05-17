"""
Beta testing routes for handling beta access requests and management
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import current_user, login_required
from models import User, BetaTester, db
from utils.beta_test_helper import (
    is_beta_tester,
    register_beta_tester,
    get_beta_tester_stats,
    validate_beta_access_code,
    deactivate_beta_tester,
)
from datetime import datetime

# Create the blueprint
beta = Blueprint('beta', __name__, url_prefix='/beta')

@beta.route('/request')
def request_access():
    """Show beta access request page"""
    # If user is already a beta tester, redirect to features
    if current_user.is_authenticated and is_beta_tester(current_user.id):
        flash("You already have beta access!", "info")
        return redirect(url_for('beta.features'))
    
    # Get beta tester stats
    stats = get_beta_tester_stats()
    
    return render_template('beta/request_access.html', 
                          stats=stats, 
                          slots_available=stats['available_slots'] > 0)

@beta.route('/request', methods=['POST'])
@login_required
def submit_access_request():
    """Process beta access request"""
    access_code = request.form.get('access_code', '').strip()
    agreement = request.form.get('agreement') == 'on'
    
    if not agreement:
        flash("You must agree to provide feedback to join the beta program.", "warning")
        return redirect(url_for('beta.request_access'))
    
    # Validate access code
    if not validate_beta_access_code(access_code):
        flash("Invalid beta access code. Please check and try again.", "danger")
        return redirect(url_for('beta.request_access'))
    
    # Register the user as a beta tester
    result = register_beta_tester(
        current_user.id, 
        access_code=access_code,
        notes=f"Manual request via web form on {datetime.utcnow().strftime('%Y-%m-%d')}"
    )
    
    if result.get('success'):
        flash("Welcome to the beta program! You now have access to all beta features.", "success")
        return redirect(url_for('beta.features'))
    else:
        flash(f"Error: {result.get('error')}", "danger")
        return redirect(url_for('beta.request_access'))

@beta.route('/features')
@login_required
def features():
    """Show beta features page"""
    # Check if user is a beta tester
    if not is_beta_tester(current_user.id):
        flash("You need beta tester access to view this page.", "warning")
        return redirect(url_for('beta.request_access'))
    
    return render_template('beta/features.html')

@beta.route('/leave', methods=['POST'])
@login_required
def leave_beta():
    """Allow user to leave beta program"""
    reason = request.form.get('reason', 'User-initiated departure')
    
    # Deactivate beta status
    result = deactivate_beta_tester(current_user.id, reason)
    
    if result.get('success'):
        flash("You have been removed from the beta program. Thank you for your participation!", "success")
    else:
        flash(f"Error: {result.get('error')}", "danger")
    
    return redirect(url_for('index'))

# Admin-only routes for beta tester management
@beta.route('/admin')
@login_required
def admin():
    """Admin dashboard for beta tester management"""
    # Check if user is an admin
    if not current_user.is_administrator():
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('index'))
    
    # Get all beta testers
    from utils.beta_test_helper import get_beta_testers
    active_testers = get_beta_testers(include_inactive=False)
    inactive_testers = get_beta_testers(include_inactive=True)
    stats = get_beta_tester_stats()
    
    return render_template('beta/admin.html', 
                          active_testers=active_testers,
                          inactive_testers=inactive_testers,
                          stats=stats)