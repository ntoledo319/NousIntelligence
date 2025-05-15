"""
Beta testing routes
All routes are prefixed with /beta
"""

import json
import datetime
import os
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

# Import database from the app
from app import db

# Import beta testing models and helpers
from models import BetaTester, BetaFeedback, User
from utils.beta_test_helper import (
    is_beta_tester, requires_beta_access, register_beta_tester,
    deactivate_beta_tester, get_beta_testers, get_beta_tester_stats,
    validate_beta_access_code
)

beta_bp = Blueprint('beta', __name__, url_prefix='/beta')

# Helper to get user_id from current_user
def get_user_id():
    return str(current_user.id) if current_user.is_authenticated else None

# Beta test dashboard
@beta_bp.route('/')
@login_required
def dashboard():
    """Beta test dashboard"""
    user_id = get_user_id()
    
    # Check if user is a beta tester
    if not is_beta_tester(user_id) and not current_user.is_administrator():
        return redirect(url_for('beta.request_access'))
        
    # Get beta tester info
    tester = BetaTester.query.filter_by(user_id=user_id).first()
    
    # Get user's feedback
    feedback = []
    if tester:
        feedback = BetaFeedback.query.filter_by(tester_id=tester.id).order_by(
            BetaFeedback.created_at.desc()).all()
    
    # For admin users, show beta tester stats
    stats = None
    all_testers = None
    recent_feedback = None
    if current_user.is_administrator():
        stats = get_beta_tester_stats()
        all_testers = get_beta_testers(include_inactive=True)
        
        # Get recent feedback from all users
        recent_feedback = BetaFeedback.query.order_by(
            BetaFeedback.created_at.desc()).limit(10).all()
    
    return render_template('beta/dashboard.html',
                          tester=tester,
                          feedback=feedback,
                          stats=stats,
                          all_testers=all_testers,
                          recent_feedback=recent_feedback)

# Request beta access
@beta_bp.route('/request', methods=['GET', 'POST'])
@login_required
def request_access():
    """Request beta tester access"""
    user_id = get_user_id()
    
    # Check if user is already a beta tester
    if is_beta_tester(user_id):
        flash("You are already registered as a beta tester", "info")
        return redirect(url_for('beta.dashboard'))
        
    # Get current stats
    stats = get_beta_tester_stats()
    
    if request.method == 'POST':
        # Check if we've reached max capacity
        if stats['active'] >= stats['max'] and not current_user.is_administrator():
            flash(f"Sorry, we've reached our maximum capacity of {stats['max']} beta testers", "error")
            return render_template('beta/request.html', stats=stats)
        
        # Get form data
        access_code = request.form.get('access_code')
        notes = request.form.get('notes')
        
        # Admin users bypass access code check
        valid_code = current_user.is_administrator()
        
        # Validate access code if not an admin
        if not valid_code:
            valid_code = validate_beta_access_code(access_code)
            
        if valid_code:
            # Register user as beta tester
            result = register_beta_tester(user_id, access_code, notes)
            
            if result.get('success'):
                flash("You've been registered as a beta tester!", "success")
                return redirect(url_for('beta.dashboard'))
            else:
                flash(f"Error registering as beta tester: {result.get('error')}", "error")
        else:
            flash("Invalid beta access code", "error")
            
    return render_template('beta/request.html', stats=stats)

# Submit feedback
@beta_bp.route('/feedback', methods=['GET', 'POST'])
@login_required
@requires_beta_access
def submit_feedback():
    """Submit beta test feedback"""
    user_id = get_user_id()
    
    # Get beta tester info
    tester = BetaTester.query.filter_by(user_id=user_id).first()
    
    if not tester:
        flash("You must be a registered beta tester to submit feedback", "error")
        return redirect(url_for('beta.request_access'))
    
    if request.method == 'POST':
        # Get form data
        category = request.form.get('category', 'general')
        title = request.form.get('title')
        description = request.form.get('description')
        severity = int(request.form.get('severity', 3))
        browser = request.form.get('browser')
        device = request.form.get('device')
        
        # Validate required fields
        if not title or not description:
            flash("Title and description are required", "error")
            return render_template('beta/feedback.html')
            
        # Process screenshots if any
        screenshots = None
        if 'screenshots' in request.files:
            filenames = []
            
            # TODO: Implement file upload handling
            # For now, just store the filenames
            for file in request.files.getlist('screenshots'):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filenames.append(filename)
                    
            if filenames:
                screenshots = json.dumps(filenames)
        
        # Create feedback entry
        feedback = BetaFeedback(
            tester_id=tester.id,
            category=category,
            title=title,
            description=description,
            severity=severity,
            browser=browser,
            device=device,
            screenshots=screenshots,
        )
        
        # Save to database
        db.session.add(feedback)
        
        # Update tester stats
        tester.feedback_count += 1
        tester.last_activity = datetime.datetime.utcnow()
        
        db.session.commit()
        
        flash("Thank you for your feedback!", "success")
        return redirect(url_for('beta.dashboard'))
    
    return render_template('beta/feedback.html')

# View feedback details
@beta_bp.route('/feedback/<int:feedback_id>')
@login_required
@requires_beta_access
def view_feedback(feedback_id):
    """View feedback details"""
    user_id = get_user_id()
    
    # Get feedback entry
    feedback = BetaFeedback.query.get_or_404(feedback_id)
    
    # Get associated tester
    tester = BetaTester.query.get(feedback.tester_id)
    
    # Check if user has permission to view this feedback
    # (must be the submitter or an admin)
    if tester.user_id != user_id and not current_user.is_administrator():
        flash("You don't have permission to view this feedback", "error")
        return redirect(url_for('beta.dashboard'))
    
    return render_template('beta/view_feedback.html', 
                         feedback=feedback, 
                         tester=tester,
                         is_admin=current_user.is_administrator())

# Admin: Update feedback status
@beta_bp.route('/feedback/<int:feedback_id>/status', methods=['POST'])
@login_required
def update_feedback_status(feedback_id):
    """Update feedback status (admin only)"""
    if not current_user.is_administrator():
        flash("You don't have permission to update feedback status", "error")
        return redirect(url_for('beta.dashboard'))
    
    # Get feedback entry
    feedback = BetaFeedback.query.get_or_404(feedback_id)
    
    # Update status
    status = request.form.get('status')
    admin_notes = request.form.get('admin_notes')
    
    if status:
        feedback.status = status
        
    if admin_notes:
        feedback.admin_notes = admin_notes
        
    db.session.commit()
    
    flash("Feedback status updated", "success")
    return redirect(url_for('beta.view_feedback', feedback_id=feedback_id))

# Admin: Manage beta testers
@beta_bp.route('/admin/testers')
@login_required
def manage_testers():
    """Manage beta testers (admin only)"""
    if not current_user.is_administrator():
        flash("You don't have permission to manage beta testers", "error")
        return redirect(url_for('beta.dashboard'))
    
    # Get all testers with their user info
    testers = BetaTester.query.all()
    
    # Get stats
    stats = get_beta_tester_stats()
    
    return render_template('beta/manage_testers.html',
                          testers=testers,
                          stats=stats)

# Admin: Update tester status
@beta_bp.route('/admin/testers/<int:tester_id>/status', methods=['POST'])
@login_required
def update_tester_status(tester_id):
    """Update tester status (admin only)"""
    if not current_user.is_administrator():
        flash("You don't have permission to update tester status", "error")
        return redirect(url_for('beta.dashboard'))
    
    # Get tester
    tester = BetaTester.query.get_or_404(tester_id)
    
    # Update status
    status = request.form.get('status')
    notes = request.form.get('notes')
    
    if status == 'active':
        tester.status = 'active'
        tester.activated_at = datetime.datetime.utcnow()
        tester.deactivated_at = None
    elif status == 'inactive':
        tester.status = 'inactive'
        tester.deactivated_at = datetime.datetime.utcnow()
    
    if notes:
        tester.notes = notes
        
    db.session.commit()
    
    flash("Tester status updated", "success")
    return redirect(url_for('beta.manage_testers'))

# Admin: Feedback report
@beta_bp.route('/admin/feedback')
@login_required
def feedback_report():
    """View feedback report (admin only)"""
    if not current_user.is_administrator():
        flash("You don't have permission to view the feedback report", "error")
        return redirect(url_for('beta.dashboard'))
    
    # Get all feedback entries
    feedback = BetaFeedback.query.order_by(BetaFeedback.created_at.desc()).all()
    
    # Calculate stats
    categories = {}
    statuses = {}
    severity_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    
    for f in feedback:
        # Count by category
        if f.category in categories:
            categories[f.category] += 1
        else:
            categories[f.category] = 1
            
        # Count by status
        if f.status in statuses:
            statuses[f.status] += 1
        else:
            statuses[f.status] = 1
            
        # Count by severity
        severity_counts[f.severity] += 1
    
    stats = {
        'total': len(feedback),
        'categories': categories,
        'statuses': statuses,
        'severity': severity_counts
    }
    
    return render_template('beta/feedback_report.html',
                          feedback=feedback,
                          stats=stats)